Setup virtualenv:

	1. Faça o setup do virtualenv do python nesta pasta python-scripts
	   Siga o tutorial: https://www.treinaweb.com.br/blog/criando-ambientes-virtuais-para-projetos-python-com-o-virtualenv
	
	2. Ative o seu virtualenv
	
	3. Rode o comando
		pip3 install -r ./requirements.txt

Para executar:

1. Coloque os arquivos raw, pro ou ave no diretório input/MRR/data

2. execute o comando:
        ./<pasta-venv>/bin/python3 MRR_gen_netCDF.py --help

3. leia as instruções e execute o comando com a flag desejada

após finalizar o processamento dos arquivos brutos para netCDF é possível prosseguir para a geração de figuras

4. execute o comando:
        ./<pasta-venv>/bin/python3 MRR_gen_figures.py --help

3. leia as instruções e execute o comando com a flag desejada