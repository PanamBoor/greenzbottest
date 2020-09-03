# Обозначаем слова, которые отвечают за доход и за расход ( или же в долг, пока нет )

dohod_sinonims = 'работа, зарплата, бизнес, продажа бизнеса'

# Получаемое искомое слово
find_word = input()

# Делим строку синонимов, чтобы проверить это в доход, в расход, в долг или не в разобранное
sort_dohod_sinonims = dohod_sinonims.split(', ')
print('Делим слова через запятую: ' + str(sort_dohod_sinonims))

# Проверяем есть ли такой синоним в доходе
if sort_dohod_sinonims.count(find_word)>0:
	print('Eto dohod!')
else:
	print('Ne dohod')


