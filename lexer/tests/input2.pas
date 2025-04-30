PROGRAM TestMath;
VAR
  x, y, result : INTEGER;

BEGIN
  x := 10;
  y := 20;

  { Проверим условие }
  IF x < y THEN
    result := x + y
  ELSE
    result := x - y;

  // Печать результата
  writeln('Result: ', result);
END.
