-- Misc. Extensions
--

function incr(key, value)
   value = tonumber(value)
   if not value then
      return nil
   end
   local old = tonumber(_get(key))
   if old then
      value = value + old
   end
   if not _put(key, value) then
      return nil
   end
   return value
end


-- List functions
-- 
--

LIST_DELIM = "~"

function _current_list(key, cur)
   local old = _get(key)

   if old then
       old = string.gsub(old, cur, "")

       return _tokenize(old, LIST_DELIM)
    else
        return false
   end
end


function list_add(key, value)
    local current = _current_list(key, value)

    if current == false then
        current = {}
    end

    local tokens = _tokenize(value, LIST_DELIM)
    for i = 1, #tokens do
        table.insert(current, tokens[i])
    end

    -- Filter list and remove too many
    local index = 1
    if table.getn(current) > 200 then
        index = table.getn(current) - 151
    end

    local result = {}
    for i = index, #current do
        table.insert(result, current[i])
    end

    local str_result = strjoin("~", result)
    _put(key, str_result)

    return "ok"
end


function list_remove(key, value)
    local current = _get(key)

    if not current then
        return "ok"
    end

    local tokens = _tokenize(value, LIST_DELIM)

    for i = 1, #tokens do
        current = string.gsub(current, tokens[i] .. "~", "")
    end

    _put(key, current)

    return "ok"
end



-- Helpers
--

function _tokenize(text, delims) 
    local tokens = {} 
    for token in string.gmatch(text, "[^" .. delims .. "]+") do 
       if #token > 0 then 
          table.insert(tokens, token) 
       end 
    end 
    return tokens 
end 

function strjoin(delimiter, list)
  local len = table.getn(list)
  if len == 0 then 
    return "" 
  end

  local string = list[1]
  for i = 2, len do 
    string = string .. delimiter .. list[i] 
  end

  return string .. delimiter
end
