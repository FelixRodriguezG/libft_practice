" Atajos de la sesión de práctica de la libft. Solo se cargan desde
" ./libft_43.sh menu (vim -S libft_vim.vim): tu .vimrc no cambia.
"   F5  guarda y testea el archivo en el menú
"   F6  tip de la función (F6 otra vez en el menú: el pseudocódigo)
"   F7  man de la función original (o su ficha del subject)

" Carpeta del script (expand('<sfile>') solo vale fuera de las funciones).
let s:dir = expand('<sfile>:p:h')

" El dibujo del «43» de la cabecera (HEADER_ART del script).
function! s:HeaderArt() abort
	let l:art = []
	let l:inside = 0
	for l:line in readfile(s:dir . '/libft_43.sh')
		if l:line =~# '^HEADER_ART=('
			let l:inside = 1
		elseif l:inside && l:line =~# '^)'
			break
		elseif l:inside
			call add(l:art, matchstr(l:line, '"\zs[^"]*\ze"'))
		endif
	endfor
	return l:art
endfunction
let s:art = s:HeaderArt()

" El plugin de cabecera de 42 reescribe al guardar la línea 4 (nombre) y
" la 9 (Updated) con el logo de 42. Este autocmd se ejecuta después del
" suyo y las vuelve a escribir con el «43», como las genera el script.
function! s:FixHeader() abort
	" Solo archivos de práctica: los que llevan el «43» en la línea 5 (el
	" plugin no la toca). Los de tus proyectos se quedan con la de 42.
	if len(s:art) < 7 || getline(9) !~# '^/\*   Updated: '
				\ || stridx(getline(5), trim(s:art[2])) < 0
		return
	endif
	let l:updated = matchstr(getline(9), 'Updated: .\{-} by \S\+')
	call setline(4, printf('/*   %-48.48s%-25.25s*/', expand('%:t'), s:art[1]))
	call setline(9, printf('/*   %-48.48s%-25.25s*/', l:updated, s:art[6]))
endfunction

" Recarga el archivo si cambia fuera de vim (por ejemplo, al crear uno nuevo).
set autoread
augroup libft43
	autocmd!
	autocmd FocusGained,BufEnter,CursorHold * silent! checktime
	autocmd BufWritePre ft_*.c call s:FixHeader()
augroup END

" El menú lee las peticiones de este archivo, junto al script.
let s:requests = s:dir . '/.libft_peticiones'

function! s:Request(cmd) abort
	let l:name = expand('%:t:r')
	if l:name !~# '^ft_'
		echo 'Este archivo no es un ft_*.c'
		return
	endif
	call writefile([a:cmd . ' ' . l:name], s:requests, 'a')
	echo 'Menú: ' . a:cmd . ' ' . l:name
endfunction

nnoremap <silent> <F5> :update<CR>:call <SID>Request('test')<CR>
inoremap <silent> <F5> <Esc>:update<CR>:call <SID>Request('test')<CR>
nnoremap <silent> <F6> :call <SID>Request('tip')<CR>
inoremap <silent> <F6> <Esc>:call <SID>Request('tip')<CR>
nnoremap <silent> <F7> :call <SID>Request('man')<CR>
inoremap <silent> <F7> <Esc>:call <SID>Request('man')<CR>
