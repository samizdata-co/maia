--[[
Spell checks a document's prose with Hunspell on every render and preview, and warns about
words it does not recognise, with their line and suggestions.

The language comes from the document's `lang` (en-GB or ro); a span or div with its own
`lang` attribute (`[text]{lang=ro}`) is checked in that language, and one with the
`nospell` class (`[text]{.nospell}`) is not checked. Code, maths, citations, URLs and
all-caps acronyms are skipped.

Accepted words: one per line in WORDLIST at the project root (a lowercase entry also
accepts capitalised forms), plus the document's own `spellcheck: ignore:` list.

Options, in a document's YAML or in _quarto.yml:

  spellcheck: false          # do not check
  spellcheck:
    ignore: [Iohannis, Chișinăului]
    fail: true               # stop the render when there are possible mistakes
]]

local DICTIONARIES = { en = 'en_GB', ro = 'ro_RO' }
local MAX_SUGGESTIONS = 3

local function stringify(value)
  return pandoc.utils.stringify(value)
end

-- Letters, including accented and non-Latin ones; not digits, punctuation or spaces.
local function is_letter(cp)
  if cp < 0x80 then
    return (cp >= 65 and cp <= 90) or (cp >= 97 and cp <= 122)
  end
  if cp < 0xC0 or cp == 0xD7 or cp == 0xF7 then return false end
  if cp >= 0x2000 and cp <= 0x206F then return false end -- general punctuation and spaces
  if cp >= 0x3000 and cp <= 0x303F then return false end
  return true
end

local APOSTROPHE, CURLY_APOSTROPHE, HYPHEN = 0x27, 0x2019, 0x2D

local function is_word_char(cp)
  return is_letter(cp) or cp == APOSTROPHE or cp == CURLY_APOSTROPHE
end

-- Words in one Str element. Tokens that look like numbers, handles, paths, file names,
-- domains or abbreviations with dots are skipped whole.
local function words_in(text)
  local words = {}
  if text:find('[%d@/_\\#]') or text:find('%a%.%a') then return words end
  local current = {}
  local function flush()
    while #current > 0 and not is_letter(current[1]) do table.remove(current, 1) end
    while #current > 0 and not is_letter(current[#current]) do table.remove(current) end
    if #current > 1 then
      local word = utf8.char(table.unpack(current))
      local upper = pandoc.text.upper(word)
      if word ~= upper or word == pandoc.text.lower(word) then -- skip acronyms like NATO
        words[#words + 1] = word
      end
    end
    current = {}
  end
  for _, cp in utf8.codes(text) do
    if is_letter(cp) or cp == APOSTROPHE or cp == HYPHEN then
      current[#current + 1] = cp
    elseif cp == CURLY_APOSTROPHE then
      current[#current + 1] = APOSTROPHE -- smart quotes turn ' into ’; the source has '
    else
      flush()
    end
  end
  flush()
  return words
end

-- Words to check, by language code: words[lang] is a list, seen[lang] a set.
local words, seen = {}, {}

local function add(lang, text)
  for _, word in ipairs(words_in(text)) do
    if not seen[lang] then seen[lang], words[lang] = {}, {} end
    if not seen[lang][word] then
      seen[lang][word] = true
      table.insert(words[lang], word)
    end
  end
end

local function skip() return nil, false end

local function collect(list, lang)
  local function scoped(el)
    if el.classes:includes('nospell') then return nil, false end
    local own = el.attributes.lang
    if own and own ~= lang then
      collect(el.content, own)
      return nil, false
    end
  end
  list:walk({
    traverse = 'topdown',
    Str = function(el) add(lang, el.text) end,
    Span = scoped,
    Div = scoped,
    Cite = skip,
    Code = skip,
    CodeBlock = skip,
    Math = skip,
    RawInline = skip,
    RawBlock = skip,
  })
end

local function collect_meta(value, lang)
  local kind = pandoc.utils.type(value)
  if kind == 'Inlines' or kind == 'Blocks' then
    collect(value, lang)
  elseif kind == 'string' then
    add(lang, value)
  elseif kind == 'List' then
    for _, item in ipairs(value) do collect_meta(item, lang) end
  end
end

-- Accepted words from WORDLIST and the document's ignore list.
local function accepted_words(project_dir, options)
  local exact, folded = {}, {}
  local function accept(entry)
    entry = entry:gsub('’', "'"):match('^%s*(.-)%s*$')
    if entry == '' or entry:sub(1, 1) == '#' then return end
    exact[entry] = true
    if entry == pandoc.text.lower(entry) then folded[entry] = true end
  end
  local file = io.open(pandoc.path.join({ project_dir, 'WORDLIST' }), 'r')
  if file then
    for line in file:lines() do accept(line) end
    file:close()
  end
  if type(options) == 'table' and options.ignore then
    local ignore = options.ignore
    if pandoc.utils.type(ignore) ~= 'List' then ignore = { ignore } end
    for _, entry in ipairs(ignore) do accept(stringify(entry)) end
  end
  return function(word)
    return exact[word] or folded[pandoc.text.lower(word)]
  end
end

local function hunspell(dictionary, list)
  local input = {}
  for _, word in ipairs(list) do input[#input + 1] = '^' .. word end -- ^ stops pipe commands
  local ok, output = pcall(pandoc.pipe, 'hunspell',
    { '-a', '-i', 'UTF-8', '-d', dictionary }, table.concat(input, '\n') .. '\n')
  if not ok then return nil, tostring(output) end
  local issues, reported = {}, {}
  for line in output:gmatch('[^\n]+') do
    local word, suggestions = line:match('^& (%S+) %d+ %d+: (.*)$')
    if not word then word = line:match('^# (%S+) %d+$') end
    if word and not reported[word] then
      reported[word] = true
      local list = {}
      for suggestion in (suggestions or ''):gmatch('[^,]+') do
        if #list < MAX_SUGGESTIONS then list[#list + 1] = suggestion:match('^%s*(.-)%s*$') end
      end
      issues[#issues + 1] = { word = word, suggestions = list }
    end
  end
  return issues
end

-- The source file's lines with code blocks, inline code and link targets blanked out,
-- so a word is found where it appears in prose.
local function source_lines(path)
  local file = path and io.open(path, 'r')
  if not file then return {} end
  local lines, fence = {}, nil
  for line in file:lines() do
    local marker = line:match('^%s*(```+)') or line:match('^%s*(~~~+)')
    if fence then
      if marker and marker:sub(1, 1) == fence:sub(1, 1) and #marker >= #fence then fence = nil end
      line = ''
    elseif marker then
      fence, line = marker, ''
    else
      local blank = function(s) return string.rep(' ', #s) end
      line = line:gsub('`[^`]*`', blank):gsub('%]%b()', function(s) return ']' .. blank(s:sub(2)) end)
    end
    lines[#lines + 1] = line
  end
  file:close()
  return lines
end

local function codepoint_before(line, i)
  if i < 1 then return nil end
  local start = i
  while start > 1 and line:byte(start) >= 0x80 and line:byte(start) < 0xC0 do start = start - 1 end
  local ok, cp = pcall(utf8.codepoint, line, start)
  return ok and cp or nil
end

local function codepoint_at(line, i)
  if i > #line then return nil end
  local ok, cp = pcall(utf8.codepoint, line, i)
  return ok and cp or nil
end

-- First line and column (in characters) where the word appears on its own.
local function locate(lines, word)
  local variants = { word }
  if word:find("'") then variants[2] = word:gsub("'", '’') end
  for number, line in ipairs(lines) do
    for _, variant in ipairs(variants) do
      local from = 1
      while true do
        local s, e = line:find(variant, from, true)
        if not s then break end
        local before, after = codepoint_before(line, s - 1), codepoint_at(line, e + 1)
        if not (before and is_word_char(before)) and not (after and is_word_char(after)) then
          return number, (utf8.len(line, 1, s - 1) or (s - 1)) + 1
        end
        from = e + 1
      end
    end
  end
end

local function dictionary_key(lang)
  local base = lang and lang:lower():match('^(%a+)')
  return base and DICTIONARIES[base] and base or nil
end

local warned_missing = false

return {
  {
    Pandoc = function(doc)
      local options = doc.meta.spellcheck
      if options == false then return nil end

      local input = quarto.doc.input_file
      local project_dir = (quarto.project and quarto.project.directory)
        or (input and pandoc.path.directory(input)) or '.'
      local lang = doc.meta.lang and stringify(doc.meta.lang) or 'en-GB'

      for _, field in ipairs({ 'title', 'subtitle', 'abstract', 'description' }) do
        if doc.meta[field] then collect_meta(doc.meta[field], lang) end
      end
      collect(doc.blocks, lang)

      local is_accepted = accepted_words(project_dir, options)
      local directory = pandoc.path.join({ pandoc.path.directory(PANDOC_SCRIPT_FILE), 'dictionaries' })
      local lines = source_lines(input)
      local found, skipped = {}, {}

      -- Group the collected languages by dictionary (en, en-GB and en-US all use en_GB).
      local by_key = {}
      for code, list in pairs(words) do
        local key = dictionary_key(code)
        if key then
          by_key[key] = by_key[key] or { label = code, words = {} }
          for _, word in ipairs(list) do
            if not is_accepted(word) then table.insert(by_key[key].words, word) end
          end
        else
          table.insert(skipped, code)
        end
      end

      for key, group in pairs(by_key) do
        if #group.words > 0 then
          local issues, err = hunspell(pandoc.path.join({ directory, DICTIONARIES[key] }), group.words)
          if not issues then
            if not warned_missing then
              warned_missing = true
              local reason = err:find('does not exist') and 'it is not installed' or err
              quarto.log.warning('spellcheck: could not run hunspell (' .. reason .. '), so spelling'
                .. ' was not checked. Install it with `sudo apt install hunspell` or `brew install hunspell`.')
            end
          else
            for _, issue in ipairs(issues) do
              if not is_accepted(issue.word) then
                issue.label = group.label
                issue.line, issue.column = locate(lines, issue.word)
                found[#found + 1] = issue
              end
            end
          end
        end
      end

      for _, code in ipairs(skipped) do
        quarto.log.warning('spellcheck: no dictionary for lang "' .. code .. '", so its text was not checked.')
      end
      if #found == 0 then return nil end

      table.sort(found, function(a, b)
        if (a.line or math.huge) ~= (b.line or math.huge) then
          return (a.line or math.huge) < (b.line or math.huge)
        end
        if (a.column or 0) ~= (b.column or 0) then return (a.column or 0) < (b.column or 0) end
        return a.word < b.word
      end)

      local path = input and pandoc.path.make_relative(input, project_dir) or 'document'
      local report = {}
      for _, issue in ipairs(found) do
        local where = issue.line and (path .. ':' .. issue.line .. ':' .. issue.column)
          or (path .. ' (generated text)')
        local hint = #issue.suggestions > 0 and (' → ' .. table.concat(issue.suggestions, ', ')) or ''
        report[#report + 1] = '  ' .. where .. '  ' .. issue.word .. hint .. '  [' .. issue.label .. ']'
      end
      local summary = string.format('spellcheck: %d possible spelling %s in %s',
        #found, #found == 1 and 'mistake' or 'mistakes', path)
      quarto.log.warning(summary .. '\n' .. table.concat(report, '\n')
        .. '\n  Add correct words to WORDLIST, or to `spellcheck: ignore:` in the document.')

      if type(options) == 'table' and options.fail then
        -- Quarto reports a filter's error() but still finishes the render, so exit instead.
        io.stderr:write('spellcheck: stopping the render (`spellcheck: fail: true`).\n')
        os.exit(1)
      end
      return nil
    end,
  },
}
