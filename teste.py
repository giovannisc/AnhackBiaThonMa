from flask import Flask, escape, request
import os
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
import pandas as pd
import csv
import json
import requests

admin = {'itau':['462.563.876/0001-45' , '075.344.618/0001-91'], 'bradesco':['075.344.618/0001-90', '462.563.876/0001-47', '462.563.876/0001-48'], 'mellon': ['462.563.876/0001-46', '075.344.618/0001-92', '075.344.618/0001-93']}
titulo = {'itau': ["Valor", "Tipo", "ID"], 'bradesco': ["Tipo de Movimentação", "Valor", 'CNPJ'], "mellon": ["Valor da movimentação", "Tipo de aplicação", "ID_CLiente", "CNPJ"] }
def which_admin(cnpj):
	for k in admin.keys():
		if cnpj in admin[k]:
			return k

UPLOAD_FOLDER = '/home/giovanni/Documents/hackAnbima/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'xlsx', 'json', 'csv'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
		return '.' in filename and \
				   filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/itau', methods=['POST','GET'])
def itau():
	if request.method == 'POST':
		# check if the post request has the file part
		if 'update_file' not in request.files:
			flash('No file part')
			return redirect(request.url)
		file = request.files['update_file']
		# if user does not select file, browser also
		# submit an empty part without filename
		if file.filename == '':
			flash('No selected file')
			return redirect(request.url)
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER']+"itau", filename))
			print(file.filename)
			return "file received by itau", 200
	return "failed", 203

@app.route('/bradesco', methods=['POST','GET'])
def bradesco():
	if request.method == 'POST':
		# check if the post request has the file part
		if 'update_file' not in request.files:
			flash('No file part')
			return redirect(request.url)
		file = request.files['update_file']
		# if user does not select file, browser also
		# submit an empty part without filename
		if file.filename == '':
			flash('No selected file')
			return redirect(request.url)
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER']+"bradesco", filename))
			print(file.filename)
			return "file received by bradesco", 200
	return "failed", 203

@app.route('/mellon', methods=['POST','GET'])
def mellon():
	if request.method == 'POST':
		# check if the post request has the file part
		if 'update_file' not in request.files:
			flash('No file part')
			return redirect(request.url)
		file = request.files['update_file']
		# if user does not select file, browser also
		# submit an empty part without filename
		if file.filename == '':
			flash('No selected file')
			return redirect(request.url)
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER']+"mellon", filename))
			return "file received by mellon", 200
	return "failed", 203

@app.route('/openfile', methods=['POST', 'GET'])
def openfile():
	if request.method == 'POST':
		file = request.files['userfile']
		if file.filename == '':
			flash('No selected file')
			return redirect(request.url)
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			df = pd.read_excel(os.path.join(app.config['UPLOAD_FOLDER'], filename)) #for an earlier version of Excel, you may need to use the file extension of 'xls'
			ADMS = {'itau': [], 'bradesco':[], 'mellon':[]}
			i = 0
			for cnpj in df['CNPJ_Fundo']:
				ADMS[which_admin(cnpj)].append([df['ID_Cliente'][i], df['Valor_movimentação'][i], df['CNPJ_Fundo'][i], df['Tipo_Movimentação'][i]])
				i+=1
			with open('ordemItau.csv', 'w') as file:
				writer = csv.writer(file, delimiter=',',
										quotechar='|', quoting=csv.QUOTE_MINIMAL)
				writer.writerow(titulo['itau'][:])
				for i in ADMS['itau']:
					a=[i[1], i[3], i[0]]
					writer.writerow(a[:])
			bradescoFile = {}
			for t in titulo['bradesco']:
				bradescoFile[t] = []
			for e in ADMS['bradesco']:
				i=0
				for t in titulo['bradesco']:
					if i == 0:
						bradescoFile[t].append(e[3])
					if i == 1:
						bradescoFile[t].append(str(e[1]))
					if i == 2:
						bradescoFile[t].append(e[2])
					i+=1
			with open('ordemBradesco.json', 'w') as f:
				json.dump(bradescoFile, f)
			with open('ordemMellon.txt', 'w') as f:
				mstring = titulo['mellon'][0]+" "+titulo['mellon'][1]+" "+titulo['mellon'][2]+" "+titulo['mellon'][3]+"\n"
				for e in ADMS['mellon']:
					mstring += str(e[1]) + " " + e[3] + " " + str(e[0]) + " " + e[2] + "\n"
				f.write(mstring)
			tableElement = []
			for k in ADMS.keys():
				for e in ADMS[k]:
					tableElement.append("""
						<thead>
			            <tr class="table-secondary">
			              <th scope="col">//0</th>
			              <th scope="col">//1</th>
			              <th scope="col">//2</th>
			              <th scope="col">//3</th>
			              <th scope="col">//4</th>
			            </tr>
				""")
					tableElement[-1] = tableElement[-1].replace('//4', k)
					print(k,e)
					for j in e:
						tableElement[-1] = tableElement[-1].replace("//"+str(e.index(j)),str(j))				
			table = """
					<div style="margin-bottom: 50px; font-size: 25px"> Dados coletados </div>
					<table style="padding-left: 320px">
		          <thead>
		            <tr">
		              <th scope="col">Cod. Cliente</th>
		              <th scope="col">VL. Aplicação</th>
		              <th scope="col">Fundo</th>
		              <th scope="col">Tipo</th>
		              <th scope="col">Administrador</th>
		            </tr>

			"""
			for i in tableElement:
				table += "\n"+i
			table += "\n </table>"
	return open('secondPage.html','r').read().format(table), 200

@app.route('/', methods=['GET'])
def root():
	return open('index.html','r').read(), 200

@app.route('/sendfiles', methods=['GET'])
def sendfile():
	url = {}
	url[0] = 'http://localhost:5000/itau'
	url[1] = 'http://localhost:5000/bradesco'
	url[2] = 'http://localhost:5000/mellon'
	files = {}
	files[0] = {'update_file': open('ordemItau.csv', 'rb')}
	files[1] = {'update_file': open('ordemBradesco.json', 'rb')}
	files[2] = {'update_file': open('ordemMellon.txt', 'rb')}
	for i in range(3):
		requests.post(url=url[i], files=files[i])
	return open('thirdPage.html','r').read(), 200
if __name__ == '__main__':
	app.secret_key = 'super secret key'
	app.config['SESSION_TYPE'] = 'filesystem'

	app.run(debug=False, host="::", port=5000)