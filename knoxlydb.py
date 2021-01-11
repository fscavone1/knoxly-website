import csv
import pandas as pd
import random as rnd
import random
import cleantweet as ct

datasets = ['./datasets/Health.csv', './datasets/Health2.csv', './datasets/Job.csv', './datasets/Politics.csv', 
			'./datasets/Racism.csv', './datasets/Religion.csv', './datasets/Sexual Orientation.csv', './datasets/Travel.csv']
datasets200 = ['./datasets/200/Health.csv', './datasets/200/Job.csv', './datasets/200/Politics.csv', './datasets/200/Racism.csv', 
				'./datasets/200/Religion.csv', './datasets/200/Sexual Orientation.csv', './datasets/200/Travel.csv']
row = []


def pick_random_row(dataset):
	if '2.csv' in dataset:
		topic = dataset.replace('./datasets/','').replace('2.csv', '')
	else:
		topic = dataset.replace('./datasets/','').replace('.csv', '')
		if '200/' in topic:
			topic = topic.replace('200/', '')
	with open(dataset, 'rt', encoding="utf8") as f:
		reader = csv.reader(f)
		chosen_row = random.choice(list(reader))
		#row.append(chosen_row)
		return [chosen_row, topic]


def get_from_db(type, index):
	if type == 'test':
		res = pick_random_row(datasets200[index])
	elif type == 'senstest':
		dataset = random.choice(list(datasets))
		res = pick_random_row(dataset)

	tweet = res[0]
	cleaned_row = ct.clean(tweet[1])
	row.clear()
	return [tweet[0], cleaned_row, res[1]]


def update_sensibility(id_tweet, sens):
	df = pd.read_csv('./datasets/sensibility_dataset.csv')
	index = df[df['ID']==id_tweet].index.values
	if not len(index):
		if sens == 'Sensible' or sens == 'Racist':
			new_row = {'ID':id_tweet, 'sensible_count':1, 'non_sensible_count':0}
			df = df.append(new_row, ignore_index=True)
		elif sens == 'Non-Sensible' or sens == 'Non-Racist':
			new_row = {'ID':id_tweet, 'sensible_count':0, 'non_sensible_count':1}
			df = df.append(new_row, ignore_index=True)
	else:
		if sens == 'Sensible' or sens == 'Racist':
			df.at[index[0], 'sensible_count'] += 1
		elif sens == 'Non-Sensible' or sens == 'Non-Racist':
			df.at[index[0], 'non_sensible_count'] += 1
	df.to_csv('datasets/sensibility_dataset.csv', index=False)


def check_sensibility(id_tweet, topic, guess):
	df = pd.read_csv('./datasets/200/' + topic + '.csv')
	index = df[df['ID']==id_tweet].index.values[0]
	correct_sens = df.at[index, 'sensibile']
	print(f'La sensibilità corretta è: {correct_sens}')
	if correct_sens == guess:
		return 1;
	else:
		return 0;
