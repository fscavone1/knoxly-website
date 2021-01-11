from flask import Flask, request, render_template, send_file
import knoxlydb
import uuid
import zipfile
import io
import pathlib

app = Flask(__name__)
counter = 0
correct_answers = 0
max_test = 7
user_id = uuid.uuid1()


@app.route("/")				#LINK
def home():					#PAGINA
	global counter
	counter = 0
	return render_template('index.html') #HTML


@app.route('/guidelines')
def guidelines():
	global counter
	counter = 0
	return render_template('guidelines.html')


@app.route("/senstest<id>", methods=['GET','POST'])
def senstest(id):
	global counter, racism_show, other_show

	if request.method == 'POST':
		id_tweet = request.form['id_tweet']
		sens = request.form['sens-button']
		if sens:
			knoxlydb.update_sensibility(id_tweet, sens)

	counter += 1
	tweet = knoxlydb.get_from_db("senstest", 0);
	text = ''.join(tweet[1])
	id_tweet = tweet[0]
	racism_show = 'none'
	other_show = 'inline'
	if tweet[2] == 'Racism':
		racism_show = 'inline'
		other_show = 'none'
	return render_template('senstest.html', tweet_text=text, user_id=user_id.int, id_tweet=id_tweet, id=counter, topic=tweet[2], racism_show=racism_show, other_show=other_show)


@app.route("/test<id>", methods=['GET','POST'])
def test(id):
	global counter, racism_show, other_show, correct_answers, user_id

	while counter < max_test:
		if request.method == 'POST':
			id_tweet = request.form['id_tweet']
			topic = request.form['topic']
			sens = request.form['sens-button']
			if sens:
				if sens == 'Sensible' or sens == 'Racist':
					guess = 1
				elif sens == 'Non-Sensible' or sens == 'Non-Racist':
					guess = 0
				res = knoxlydb.check_sensibility(id_tweet, topic, guess)
				correct_answers += res
				print(f'Value of res: {res} Correct answers: {correct_answers} at iteration {counter}')

		tweet = knoxlydb.get_from_db("test", counter);
		counter += 1
		text = ''.join(tweet[1])
		id_tweet = tweet[0]
		racism_show = 'none'
		other_show = 'inline'
		if tweet[2] == 'Racism':
			racism_show = 'inline'
			other_show = 'none'
		return render_template('test.html', tweet_text=text, user_id=user_id.int, id_tweet=id_tweet, id=counter, topic=tweet[2], racism_show=racism_show, other_show=other_show, pass_show='none', fail_show='none')

	if correct_answers >= 5:
		counter = 0
		return render_template('test.html', tweet_text='', user_id=user_id.int, id=0, id_tweet=0, topic='', racism_show='none', other_show='none', pass_show='inline', fail_show='none')

	else:
		counter = 0
		return render_template('test.html', tweet_text='', user_id=user_id.int, id=0, id_tweet=0, topic='', racism_show='none', other_show='none', pass_show='none', fail_show='inline')


@app.route('/download-zip')
def request_zip():
    base_path = pathlib.Path('./datasets/')
    data = io.BytesIO()
    with zipfile.ZipFile(data, mode='w') as z:
        for f_name in base_path.iterdir():
            z.write(f_name)
    data.seek(0)
    return send_file(
        data,
        mimetype='application/zip',
        as_attachment=True,
        attachment_filename='data.zip'
    )



if __name__ == "__main__":
	app.run()