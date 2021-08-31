CREATE TABLE IF NOT EXISTS quiz.USER(
user TEXT NOT NULL PRIMARY KEY,
pass TEXT NOT NULL,
type TEXT NOT NULL);

CREATE TABLE IF NOT EXISTS quiz.QUIZ(
id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
numb INTEGER NOT NULL,
release TEXT NOT NULL,
expire TEXT NOT NULL,
problem TEXT NOT NULL,
tests TEXT NOT NULL,
results TEXT NOT NULL,
diagnosis TEXT NOT NULL);

CREATE TABLE IF NOT EXISTS quiz.USERQUIZ(
id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
userid TEXT NOT NULL,
quizid INTEGER NOT NULL,
sent TEXT NOT NULL,
answer TEXT NOT NULL,
result TEXT NOT NULL);

Insert into QUIZ(numb, release, expire, problem, tests, results, diagnosis) values (1, '2018-08-01','2018-12-31 23:59:59','Exemplo de problema','[[1],[2],[3]]','[0, 0, 0]','["a","b","c"]');