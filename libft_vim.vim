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

" Autoguardado: tras unos segundos sin escribir, al cambiar de archivo y al
" pasar al menú, para no perder nada si se cierra la ventana. No guarda si el
" archivo ha cambiado fuera de vim (por ejemplo, el script acaba de crearlo
" de nuevo): así no lo pisa con lo que hubiera en vim.
set updatetime=3000
function! s:AutoSave() abort
	let l:file = expand('%:p')
	if !&modified || l:file ==# '' || &readonly || &buftype !=# ''
		return
	endif
	" La hora del archivo va por segundos: se mira también el contenido.
	if filereadable(l:file) && (getftime(l:file) != get(b:, 'libft_mtime', -1)
				\ || readfile(l:file, 'b') != get(b:, 'libft_disk', []))
		return
	endif
	silent update
endfunction
function! s:Remember() abort
	let l:file = expand('%:p')
	let b:libft_mtime = getftime(l:file)
	let b:libft_disk = filereadable(l:file) ? readfile(l:file, 'b') : []
endfunction
augroup libft43_autosave
	autocmd!
	autocmd BufReadPost,BufWritePost * call s:Remember()
	autocmd CursorHold,CursorHoldI,BufLeave,FocusLost * ++nested call s:AutoSave()
augroup END
" El archivo de la línea de órdenes se abre antes de cargar este script.
call s:Remember()

" Colores RGB (termguicolors) dentro de tmux: vim se cree en una terminal
" «screen» y, sin esto, no manda ningún color.
if &termguicolors && $TMUX !=# ''
	let &t_8f = "\<Esc>[38;2;%lu;%lu;%lum"
	let &t_8b = "\<Esc>[48;2;%lu;%lu;%lum"
endif

" Sin foco, vim se apaga: sin colores de sintaxis y con el texto en gris.
" Este vim no recibe los eventos de foco dentro de tmux, así que el menú
" deja dónde está el foco en .libft_foco y aquí se mira cada 0,3 s.
let s:focus_file = s:dir . '/.libft_foco'
let s:dimmed = 0
function! s:Dim(on) abort
	if a:on
		if &l:syntax !=# 'OFF'
			let b:libft_syntax = &l:syntax
			setlocal syntax=OFF
		endif
		setlocal wincolor=LibftDim
	else
		if exists('b:libft_syntax')
			let &l:syntax = b:libft_syntax
			unlet b:libft_syntax
		endif
		setlocal wincolor=
	endif
endfunction
function! s:CheckFocus(timer) abort
	let l:where = filereadable(s:focus_file) ? get(readfile(s:focus_file), 0, '') : ''
	let l:dim = l:where ==# 'menu' || l:where ==# 'nada'
	if l:dim != s:dimmed
		let s:dimmed = l:dim
		call s:Dim(l:dim)
	endif
endfunction
function! s:DimColors() abort
	highlight LibftDim guifg=#444444 ctermfg=238
endfunction
call s:DimColors()
augroup libft43_focus
	autocmd!
	autocmd ColorScheme * call s:DimColors()
	" El menú puede abrir otro archivo con vim sin foco.
	autocmd BufEnter * call s:Dim(s:dimmed)
augroup END
call timer_start(300, function('s:CheckFocus'), {'repeat': -1})

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
