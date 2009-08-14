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

function list_add(key, value)
    --- Determine the limit by inspecting if | is in the key
    local limit = 200

    if string.find(key, '|') then
        local key_parts = _tokenize(key, '|')
        limit = tonumber(key_parts[1])
        key = key_parts[2]
    end

    local current_value = _get(key) or ''

    --- Filter out values so we don't insert duplicates 
    local serach_val = LIST_DELIM .. current_value
    local values = _tokenize(value, LIST_DELIM)
    local filtered = {}

    for i=1, #values do
        if not string.match(serach_val, LIST_DELIM .. values[i] .. LIST_DELIM) then
            table.insert(filtered, values[i])
        end
    end

    --- Check if they are all duplicates
    if #filtered == 0 then
        return "ok"
    end

    values = filtered
    value = table.concat(values, LIST_DELIM)  .. LIST_DELIM

    --- Check if we should apply cleanup
    local current_list = _current_list(current_value, nil)
    local list_size = #current_list

    --- If the size is too big then clean up in it
    list_size = list_size + #values

    if list_size > (limit + 100) then
        _list_cleanup(key, current_list, limit, #values)
    end

    --- Append values at the end of the list
    _putcat(key, value)
    return "ok"
end


function list_remove(key, value)
    local current_list = _get(key)

    if not current_list then
        return "ok"
    end

    local tokens = _tokenize(value, LIST_DELIM)

    for i = 1, #tokens do
        current_list = string.gsub(current_list, tokens[i] .. LIST_DELIM, "")
    end

    _put(key, current_list)

    return "ok"
end



--
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

function _current_list(old_list, tokens)
   if old_list then
       if tokens then
           for i = 1, #tokens do
                old_list = string.gsub(old_list, "^" .. tokens[i] .. LIST_DELIM, "")
                old_list = string.gsub(old_list, LIST_DELIM .. tokens[i] .. LIST_DELIM, LIST_DELIM)
           end
       end

       return _tokenize(old_list, LIST_DELIM)
    else
        return {}
   end
end


--- Deletes the first entries in the list
--- so there's only `limit` entires left in the list
function _list_cleanup(key, current_list, limit, new_items_size)
    local current_size = #current_list + new_items_size

    while current_size > limit do
        --remove the first item
        table.remove(current_list, 1)
        current_size = current_size - 1
    end

    _list_store(key, current_list)

    return current_size
end

function _list_store(key, list)
    local result = table.concat(list, LIST_DELIM)  .. LIST_DELIM
    _put(key, result)
end
