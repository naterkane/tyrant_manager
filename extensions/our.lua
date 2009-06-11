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

function _current_list(key, tokens)
   local old = _get(key)

   if old then
       for i = 1, #tokens do
            old = string.gsub(old, "^" .. tokens[i] .. LIST_DELIM, "")
            old = string.gsub(old, LIST_DELIM .. tokens[i] .. LIST_DELIM, LIST_DELIM)
       end

       return _tokenize(old, LIST_DELIM)
    else
        return false
   end
end


function list_add(key, value)
    --- Determine the limit by inspecting if | is in the key
    local limit = 200

    if string.find(key, '|') then
        local key_parts = _tokenize(key, '|')
        limit = tonumber(key_parts[1])
        key = key_parts[2]
    end

    --- Fetch the current or create a new list
    local tokens = _tokenize(value, LIST_DELIM)
    local current = _current_list(key, tokens)

    if current == false then
        current = {}
    end

    --- Insert the new elements and remove the old if the size is too big
    local insert_index = 1
    for i = 1, #tokens do
        table.insert(current, insert_index, tokens[i])
        insert_index = insert_index + 1
        if #current > limit then
            table.remove(current)
        end
    end

    local result = table.concat(current, LIST_DELIM)
    _put(key, result .. LIST_DELIM)
    return "ok"
end


function list_remove(key, value)
    local current = _get(key)

    if not current then
        return "ok"
    end

    local tokens = _tokenize(value, LIST_DELIM)

    for i = 1, #tokens do
        current = string.gsub(current, tokens[i] .. LIST_DELIM, "")
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
