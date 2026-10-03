# Задача 2. 5 наибольших портов из /etc/protocols

## Задание
Вывести данные /etc/protocols в отформатированном и отсортированном порядке для 5 наибольших портов.

## Команда

grep -v '^#' /etc/protocols | grep -v '^$' | sort -k2 -n -r | head -5 | awk '{print $2, $1}'

## Результат
См. results/task2.txt
