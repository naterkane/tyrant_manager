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

    local size_key = key .. "size"

    local list_size = _get(size_key)

    --- If the size is not initialized, then init it
    if list_size == nil then
        local current = _current_list(key, nil)

        -- We need to reverse the current list, since
        -- the first version of lists did not use putcat
        -- to append values at the end...
        -- It added them to the front.
        if #current > 0 then
            current = _list_reverse(key, current)
        end

        list_size = #current
        _put(size_key, list_size)
    else
        list_size = tonumber(list_size)
    end

    --- If the size is too big then clean up in it
    local values = _tokenize(value, LIST_DELIM)

    if list_size > (limit+100) then
        local new_size = _list_cleanup(key, limit, #values)
        _put(size_key, new_size)
    else
        list_size = list_size + #values
        _put(size_key, list_size)
    end

    --- Append values at the end of the list
    _putcat(key, value)
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

function _current_list(key, tokens)
   local old = _get(key)

   if old then
       if tokens then
           for i = 1, #tokens do
                old = string.gsub(old, "^" .. tokens[i] .. LIST_DELIM, "")
                old = string.gsub(old, LIST_DELIM .. tokens[i] .. LIST_DELIM, LIST_DELIM)
           end
       end

       return _tokenize(old, LIST_DELIM)
    else
        return {}
   end
end

--- Deletes the first entries in the list
--- so there's only `limit` entires left in the list
function _list_cleanup(key, limit, new_items_size)
    local current = _current_list(key, nil)
    local current_size = #current + new_items_size

    while current_size > limit do
        --remove the first item
        table.remove(current, 1)
        current_size = current_size - 1
    end

    _list_store(key, current)

    return current_size
end

function _list_reverse(key, t)
	local size = #t

	local j = size
	for i = 1, size / 2 do
		t[i], t[j] = t[j], t[i]
		j = j - 1
	end

    _list_store(key, t)
    return t
end

function _list_store(key, list)
    local result = table.concat(list, LIST_DELIM)
    _put(key, result .. LIST_DELIM)
end
