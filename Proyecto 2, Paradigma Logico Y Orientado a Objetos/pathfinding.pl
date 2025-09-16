% pathfinding.pl

% Hechos dinámicos
:- dynamic(muro/2).
:- dynamic(inicio/1).
:- dynamic(fin/1).
:- dynamic(limite_x/1).
:- dynamic(limite_y/1).
:- dynamic(profundidad_maxima/1).
:- dynamic(direccion_pref/2).

% buscar_camino/2
buscar_camino(CaminoX, CaminoY) :-
    inicio(PosInicio), fin(PosFin), profundidad_maxima(MaxP),
    camino(PosInicio, PosFin, [PosInicio], CaminoInvertido, 0, MaxP),
    reverse(CaminoInvertido, CaminoNormal),
    extraer_coordenadas(CaminoNormal, CaminoX, CaminoY).

% camino/6
camino(_, _, _, _, P, Pmax) :- P >= Pmax, !, fail.
camino(Pos, Pos, _, [Pos], _, _).
camino(PosActual, PosFinal, Visitados, [PosActual | RCamino], P, Pmax) :-
    movimiento_inteligente(PosActual, PosSiguiente),
    valido(PosSiguiente),
    \+ member(PosSiguiente, Visitados),
    PosSiguiente = pos(Xs, Ys),
    \+ muro(Xs, Ys),
    P1 is P + 1,
    camino(PosSiguiente, PosFinal, [PosSiguiente | Visitados], RCamino, P1, Pmax).

% valido/1
valido(pos(X, Y)) :-
    limite_x(MaxX), limite_y(MaxY),
    X >= 0, X < MaxX, Y >= 0, Y < MaxY.

% --- LÓGICA DE MOVIMIENTO INTELIGENTE (CORREGIDA) ---
movimiento_inteligente(Pos, SiguientePos) :-
    direccion_pref(Primaria, _),
    movimiento(Primaria, Pos, SiguientePos).

movimiento_inteligente(Pos, SiguientePos) :-
    direccion_pref(_, Secundaria),
    movimiento(Secundaria, Pos, SiguientePos).

% --- REGLA CORREGIDA ---
% Quitamos el guion bajo a Primaria y Secundaria porque las usamos más de una vez.
movimiento_inteligente(Pos, SiguientePos) :-
    movimiento(Dir, Pos, SiguientePos),
    direccion_pref(Primaria, Secundaria), % Nombres de variables normales
    Dir \= Primaria,
    Dir \= Secundaria.

% movimiento/3
movimiento(arriba, pos(X,Y), pos(X, Y1)) :- Y1 is Y - 1.
movimiento(abajo, pos(X,Y), pos(X, Y1)) :- Y1 is Y + 1.
movimiento(izquierda, pos(X,Y), pos(X1, Y)) :- X1 is X - 1.
movimiento(derecha, pos(X,Y), pos(X1, Y)) :- X1 is X + 1.

% extraer_coordenadas/3
extraer_coordenadas([], [], []).
extraer_coordenadas([pos(X,Y) | RPos], [X | RX], [Y | RY]) :-
    extraer_coordenadas(RPos, RX, RY).
