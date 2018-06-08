# Alinhamento de imagens
Este relatório é parte de uma série de trabalhos da disciplina *MO443 - Introdução ao Processamento de Imagem Digital* lecionada pelo Professor Hélio Pedrini na Universidade Estadual de Campinas no primeiro semestre de 2018.

## Ambiente
O algoritmo desenvolvido necessita de um ambiente com Python 3.x instalado, além das bibliotecas *OpenCV*(https://opencv.org/), *Numpy*(http://www.numpy.org), *imutils*, *PIL* e *Pytesseract. Este ultimo é apenas uma interface para um comando do sistema operacional (SO), por isso deve estar instalado no SO a biblioteca *Tesseract Open Source OCR Engine*(https://github.com/tesseract-ocr/tesseract).
## Algoritmo
Dado o ambiente como esperado, basta rodar o código fornecido como seguinte uso:
```
alinhar.py [-h] -i INPUT [-o OUTPUT]
[-m {projection,hough}]
[-p {crop,sobel,otsu,contours,gray}]
[-c CROP]
```
em quem o argumento `-i` é o endereço da imagem de entrada para ser encontrado o texto e alinhada, `-o` é o endereço para salvar a imagem de saída, `-m` é a técnica a ser utilizada para encontrar o ângulo de rotação da imagem (Hough ou Projeção Horaizontal), `-p` são os métodos de pré-processamento a serem utilizados (permitindo uma combinação de vários entre filtro de Sobel, Otsu Threshold, recortar, encontrar contornos) e `-c` é parâmetro para definir o tamanho da janela do recorte, caso selecionado no pré-processamento.(*crop*). Utilizando `-h` mostra-se o uso e descrição do programa.
### Pre-processamento
No código foram implementadas quatro técnicas para esta etapa. Vale ressaltar que independentemente dos parâmetros de \texttt{-p} passados, sempre será feito uma conversão para escala de cinza (parâmetro \texttt{gray}), já que ambos algoritmos para encontrar o ângulo esperam imagens com uma dimensão de profundidade.\\
\begin{figure}
    \centering
    \includegraphics[scale=0.5]{sample3.png}
    \caption{Imagem de exemplo com bordas pretas fora da imagem.\label{fig:sample3}}
\end{figure}
As técnicas estão ordenadas na ordem em que são aplicadas:
#### Recorte
O parâmetro \texttt{crop} quando usado permite recortar a imagem com uma janela de 500 pixels por padrão, localizada no centro da imagem. O tamanho da janela é configurável por \texttt{-c} seguido de um número inteiro.
#### Filtro Sobel
Este filtro detector de bordas é usado quando é passado \texttt{sobel} na linha de execução do programa. Basicamente ele realça bordas usando gradiente da imagem. A função utilizada esta presente na biblioteca \emph{OpenCV}. Na Figura \ref{fig:sobel} é possível visualizar o efeito da técnica.
\begin{figure}
    \centering
    \includegraphics[scale=0.6]{sobel.png}
    \caption{Aplicação do filtro de Sobel na Figura \ref{fig:sample3}.\label{fig:sobel}}
\end{figure}
#### Otsu Threshold
Esta é uma técnica de binarização local da imagem, já implementada em \emph{OpenCV} e é ativada usando parâmetro \texttt{otsu}. É possível ver seu efeito na Figura \ref{fig:otsu}.
\begin{figure}
    \centering
    \includegraphics[scale=0.6]{binary.png}
    \caption{Aplicação do Otsu threshold na Figura \ref{fig:sample3}.\label{fig:otsu}}
\end{figure}
#### Reconhecimento de Contornos
Usando \texttt{contours} é possível melhorar o processamento identificando previamente formas, como imagens e tabelas (vide \ref{fig:com_figura} e \ref{fig:sem_figura}). As mesmas são tiradas quando reconhecidas pela função \texttt{cv2.findContours} que implementa a técnica proposta por \cite{Suzuki85}.\\
\begin{figure}
    \centering
    \includegraphics[scale=0.4]{wimage.png}
    \caption{Imagem com figuras com Otsu Threshold.\label{fig:com_figura}}
\end{figure}
\begin{figure}
    \centering
    \includegraphics[scale=0.4]{woimage.png}
    \caption{Aplicação da remoção de contornos na Figura \ref{fig:com_figura}.\label{fig:sem_figura}}
\end{figure}
Quando a imagem esta deslocada e com bordas pretas, é possível também reconhecer o formato da folha e retirar este fundo preto que poderia interferir no processamento. Como é possível ver comparando a Figura \ref{fig:sample3} e \ref{fig:contours}.\\
\begin{figure}
    \centering
    \includegraphics[scale=0.6]{contours.png}
    \caption{Aplicação da remoção de contornos na Figura \ref{fig:sample3}.\label{fig:contours}}
\end{figure}

### Detecção do Ângulo
Como é perceptível nas Figuras \ref{fig:otsu} e \ref{fig:com_figura} , as imagens que passaram por binarização usando Otsu ou Sobel ficaram com o fundo preto, isso foi feito de maneria proposital pois ambos os métodos explicados a seguir funcionam mais adequadamente com pixels relevantes (neste caso letras) tendo valor, que neste caso seria 255 e cor branca.
#### Projeção Horizontal
A técnica se baseia em rotacionar a imagem em 180 graus (pois não é possível prever se o texto esta invertido) e para cada ângulo calcular a soma dos pixels em cada linha, por isso a imagem com representatividade apenas nas letras ( fundo preto, letras brancas). O ângulo com  a linha que somasse maior valor é escolhido como ângulo de correção da imagem.\\
Como é perceptível, fundo com cor igual das letras, como na Figura \ref{fig:sample3}, e imagens tornam esse algoritmo muito suscetível a falhas. Além disso, a função utilizada para rotação (\texttt{imutils.rotate\_bound}) preenche o fundo da imagem com preto, sendo este outro motivo para inverter a cor das letras e o fundo.\\
#### Transformada de Hough
Esta transformada leva os pontos com intensidade maior que 10, na escala de 0 a 255, para outro plano discretizado por $\rho = x\times cos(\theta) + y\times sen(\theta)$. Usando o valor de $\theta$ da tabela do ponto que obtiver maior número de curvas cruzando, indicará o ângulo de inclinação do texto.\\
Este método é altamente suscetível a falhas com fundos com cor, como na Figura \ref{fig:sample3}, pois todos os pontos claros (maior que 10) serão transformados para o plano de Hough e irão influenciar na escolha do ângulo. A Figura \ref{fig:hough_orig} mostra uma faixa amarela escura que representa a influencia errada do fundo da imagem, e que consequentemente leva a escolha errada do ângulo. Já na Figura \ref{fig:hough_contours} vemos claramente que o angulo de aproximadamente 84 graus esta acumulando vários pequenos pontos amarelos, com alta concentração de curvas cruzando, sendo assim a melhor escolha.
\begin{figure}
    \centering
    \includegraphics[scale=0.6]{hough_orig.png}
    \caption{Transformada de Hough dos pixels da Figura \ref{fig:otsu} (sem remoção do fundo).\label{fig:hough_orig}}
\end{figure}
\begin{figure}
    \centering
    \includegraphics[scale=0.6]{hough_contours.png}
    \caption{Transformada de Hough dos pixels da Figura \ref{fig:contours} (com remoção do fundo).\label{fig:hough_contours}}
\end{figure}
### Detecção do Texto
É aplicado a técnica de \emph{Optical Character Recognition} (OCR) antes e depois da rotação para mostrar casos em que houve melhoria. A função utilizada da do pacote citado foi  \texttt{pytesseract.image\_to\_string}.

## Saída
Durante a execução é mostrado a imagem original ao usuário em uma janela, e em seguida as imagens de cada processo de pré-processamento selecionado.
Por fim a imagem original é rotacionada negativamente com o ângulo de inclinação encontrado.
O console mostra o texto antes e depois da rotação além do ângulo de rotação para melhorar a imagem.\\
A imagem rotacionada é salva caso na execução tenha sido passado o argumento \texttt{-o} com o caminho para o arquivo.

## Testes
Os testes mostraram que ambas as técnicas de reconhecimento da inclinação têm os mesmos resultados, contudo a Transformada de Hough implementado pelo autor precisa ser otimizada, pois o tempo de execução é muito maior que a projeção horizontal.\\
Apenas o uso de binarização (Otsu ou Sobel) foi bem eficaz em imagens com fundo sólido. Porém em testes com imagens de pior qualidade ou estruturas que não fossem apenas texto, como Figura \ref{fig:sample3} e \ref{fig:com_figura}, o desempenho dos algoritmos ficava distante do ideal.\\
Aplicando recortes no centro da imagem em alguns casos ajudou a evitar bordas com problemas, contudo caso o recorte concentrasse em uma imagem, como a Figura \ref{fig:com_figura}, existia ainda uma dificuldade para processamento.\\
Então aplicando a técnica da reconhecimento de contorno foi possível obter sucesso nas imagens de teste usando filtro de Sobel e projeção horizontal.

## Condições não tratadas
Além de não serem tratados os casos em que o ambiente não está estabelecido como descrito acima, vale ressaltar que não se verifica se o endereço da imagem passado como parâmetro é válido, o que pode resultar em erros de execução devido a objetos vazios.\\
A pasta do local de saída da imagem gerada pelo algoritmo de codificação deve existir, caso contrário a mesma não é salva.\\

## Condições tratadas
Imagens podem ser coloridas ou em escala de cinza e de diferentes extensões, já que a biblioteca trata a maioria dos formatos\footnote{\url{https://docs.opencv.org/2.4/modules/highgui/doc/reading_and_writing_images_and_video.html}}. O arquivo de saída não precisa existir, pois é criado caso não exista, com a extensão \emph{.png}. Se existir e tiver algum conteúdo, o mesmo é apagado.

## Considerações finais
O arquivo entregue contem um diretório \emph{.git} em que é possível verificar a evolução do código pelos \emph{commits\footnote{\url{https://git-scm.com/docs/gittutorial/2.2.0}}}.
Também existem imagens para teste oriundas de \url{https://www.ic.unicamp.br/~helio/imagens_inclinadas_png/}.
