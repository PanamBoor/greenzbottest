<<<<<<< HEAD
# Обозначаем слова, которые отвечают за доход и за расход ( или же в долг, пока нет )

dohod_sinonims = 'работа, бизнес, продажа бизнеса'
rashod_sinonims = 'девушка, бензин, машина'
v_dolg_sinonims = 'дал в долг, отдал в долг, закинул в долг'
kratko_dni_sinonims = 'пн, вт, ср, чт, пт, сб, вс'
kratko_month_sinonims = 'сен, окт, дек, нояб, фев, март, апр, май, июнь, июль, авг, янв'

# Получаемое сообщение на разбор.
find_word = input()

# Разбираем искомую фразы через пробел на слова.
find_word_fraze = find_word.split(' ')
print('Разобранная фраза на слова: ' + str(find_word_fraze))

# Делим строку синонимов, чтобы проверить это в доход, в расход, в долг или не в разобранное.
sort_dohod_sinonims = dohod_sinonims.split(', ')
print('Делим слова через запятую: ' + str(sort_dohod_sinonims))

sort_rashod_sinonims = rashod_sinonims.split(', ')
print('Делим слова через запятую: ' + str(sort_rashod_sinonims))

sort_v_dolg_sinonims = v_dolg_sinonims.split(', ')
print('Делим слова через запятую: ' + str(sort_v_dolg_sinonims))

sort_dni_sinonims = kratko_dni_sinonims.split(', ')
print('Делим слова через запятую: ' + str(sort_dni_sinonims))

sort_month_sinonims = kratko_month_sinonims.split(', ')
print('Делим слова через запятую: ' + str(sort_month_sinonims))

# Начинаем проверять каждое слово в листе через проверки на схожесть ключевых слов.
for element in range(0,len(find_word_fraze)):
	print(str(find_word_fraze[element]))

	# Проверяем, если число от 1 до 31, ищем месяц и записываем в дату
	if find_word_fraze[element].isalpha() == False:
		if int(find_word_fraze[element]) > 0 and int(find_word_fraze[element]) < 32:
			if sort_month_sinonims.count(find_word_fraze[element+1])>0:
				date = find_word_fraze[element] + '.' + find_word_fraze[element+1]
				print ('Eto data: ' + date)
				continue


	# Проверяем ключевое слово на месяца, чтобы записывать дату месяца ( потом должен быть поиск дня этого месяца, ПЕРЕД месяцом?)
	if sort_month_sinonims.count(find_word_fraze[element])>0:
		print('Eto mesyac: ' + str(find_word_fraze[element]))
		continue


	# Проверяем число ли данный элемент, чтобы вытянуть сумму. 
	if find_word_fraze[element].isalpha() == False:
		print('Eto chisla')
		# Проверяем, если в этом числах точка и размер из 5 символов в элементе
		if find_word_fraze[element].count('.') and len(find_word_fraze[element]) == 5:
			print('Eto den i mesyac')
		continue

	# Проверяем ключевое ли слово дней это. 
	if sort_dni_sinonims.count(find_word_fraze[element])>0:
		print('Eto den: ' + str(find_word_fraze[element]))
		continue

	# Проверяем ключевое слово вчера, чтобы записывать сразу дату с функционал этого ключевого слова.
	if find_word_fraze[element] == 'вчера':
		print('Eto bilo vchera!')
		continue

	# Проверяем ключевое слово позавчера, чтобы записывать сразу дату с функционал этого ключевого слова.
	if find_word_fraze[element] == 'позавчера':
		print('Eto bilo pozavchera!')
		continue

	# Проверяем есть ли такой синоним ( одно слово ) в доходах, расходах, долгах. 
	if sort_dohod_sinonims.count(find_word_fraze[element])>0:
		print('Eto dohod!')
		continue
	elif sort_rashod_sinonims.count(find_word_fraze[element])>0:
		print('Eto rashod')
		continue
	elif sort_v_dolg_sinonims.count(find_word_fraze[element])>0:
		print('Eto v dolg')
		continue
	else:
		print('Ne razobral (')


=======
# Обозначаем слова, которые отвечают за доход и за расход ( или же в долг, пока нет )

dohod_sinonims = 'работа, бизнес, продажа бизнеса'
rashod_sinonims = 'девушка, бензин, машина'
v_dolg_sinonims = 'дал в долг, отдал в долг, закинул в долг'
kratko_dni_sinonims = 'пн, вт, ср, чт, пт, сб, вс'

# Получаемое сообщение на разбор.
find_word = input()

# Разбираем искомую фразы через пробел на слова.
find_word_fraze = find_word.split(' ')
print('Разобранная фраза на слова: ' + str(find_word_fraze))

# Делим строку синонимов, чтобы проверить это в доход, в расход, в долг или не в разобранное.
sort_dohod_sinonims = dohod_sinonims.split(', ')
print('Делим слова через запятую: ' + str(sort_dohod_sinonims))

sort_rashod_sinonims = rashod_sinonims.split(', ')
print('Делим слова через запятую: ' + str(sort_rashod_sinonims))

sort_v_dolg_sinonims = v_dolg_sinonims.split(', ')
print('Делим слова через запятую: ' + str(sort_v_dolg_sinonims))

sort_dni_sinonims = dni_sinonims.split(', ')
print('Делим слова через запятую: ' + str(sort_dni_sinonims))

# Начинаем проверять каждое слово в листе через проверки на схожесть ключевых слов.
for element in find_word_fraze:
	print(str(element))

	# Проверяем число ли данный элемент, чтобы вытянуть сумму. 
	if element.isalpha() == False:
		print('Eto chisla')
		# Проверяем, если в этом числах точка и размер из 5 символов в элементе
		if element.count('.') and len(element) == 5:
			print('Eto den i mesyac')
		continue

	# Проверяем ключевое ли слово дней это. 
	if sort_dni_sinonims.count(element)>0:
		print('Eto den: ' + str(element))
		continue

	# Проверяем ключевое слово вчера, чтобы записывать сразу дату с функционал этого ключевого слова.
	if element == 'вчера':
		print('Eto bilo vchera!')
		continue

	# Проверяем ключевое слово позавчера, чтобы записывать сразу дату с функционал этого ключевого слова.
	if element == 'позавчера':
		print('Eto bilo pozavchera!')
		continue

	# Проверяем есть ли такой синоним ( одно слово ) в доходах, расходах, долгах. 
	if sort_dohod_sinonims.count(element)>0:
		print('Eto dohod!')
		continue
	elif sort_rashod_sinonims.count(element)>0:
		print('Eto rashod')
		continue
	elif sort_v_dolg_sinonims.count(element)>0:
		print('Eto v dolg')
		continue
	else:
		print('Ne razobral (')


	# Убираем 


>>>>>>> 696e5cd3865803da93149037f471b89b7abf62e5
