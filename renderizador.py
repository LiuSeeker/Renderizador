# Desenvolvido por: Luciano Soares <lpsoares@insper.edu.br>
# Disciplina: Computação Gráfica
# Data: 28 de Agosto de 2020

import argparse     # Para tratar os parâmetros da linha de comando
import x3d          # Faz a leitura do arquivo X3D, gera o grafo de cena e faz traversal
import interface    # Janela de visualização baseada no Matplotlib
import gpu          # Simula os recursos de uma GPU

import numpy as np
from math import sin, cos, tan
from sklearn.preprocessing import minmax_scale

TRANSFORM_STACK = []
ACTUAL = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])

TRANSFORM_STACK.append(ACTUAL)

LARGURA = 400
ALTURA = 200

COORDENADAS_TELA = np.array([[LARGURA/2, 0, 0, LARGURA/2],
                             [0, -ALTURA/2, 0, ALTURA/2],
                             [0, 0, 1, 0],
                             [0, 0, 0, 1]])

def norm_array_from_matrix(matrix):
    mat_t = matrix.T
    new_mat = np.empty([3,4])
    for i in range(len(mat_t)):
        big = -9999
        for e in mat_t[i]:
            if e > big:
                big = e
        new_mat[i] = mat_t[i]/big
    
    return new_mat.T


def polypoint2D(point, color):
    """ Função usada para renderizar Polypoint2D. """
   
    
    i = 0
    while i < len(point): #(percorre de 2 em 2 coordenadas (ponto)
        split_h = False
        split_v = False
    
        # Conta se ta entre pixels
        n_points = 1
        if point[i] % 1 == 0: #horizontal (x)
            split_h = True
            n_points *= 2
        if point[i+1] % 1 == 0: #vertical (y)
            split_v = True
            n_points *= 2
        
        # Preenche os pixels
        for _ in range(n_points):
            gpu.GPU.set_pixel(int(point[i]), int(point[i+1]), color[0]*255, color[1]*255, color[2]*255)
            if split_h:
                gpu.GPU.set_pixel(int(point[i])-1, int(point[i+1]), color[0]*255, color[1]*255, color[2]*255)
            if split_v:
                gpu.GPU.set_pixel(int(point[i]), int(point[i+1])-1, color[0]*255, color[1]*255, color[2]*255)
            if split_h and split_v:
                gpu.GPU.set_pixel(int(point[i])-1, int(point[i+1])-1, color[0]*255, color[1]*255, color[2]*255)
        i += 2
    #gpu.GPU.set_pixel(3, 1, 255, 0, 0) # altera um pixel da imagem
    # cuidado com as cores, o X3D especifica de (0,1) e o Framebuffer de (0,255)

def polyline2D(lineSegments, color):
    """ Função usada para renderizar Polyline2D. """

    x0=0
    x1=0
    
    if(lineSegments[0]>lineSegments[2]):
        x0=lineSegments[2]
        x1=lineSegments[0]
        y0=lineSegments[3]
        y1=lineSegments[1]
    else:
        x0=lineSegments[0]
        x1=lineSegments[2]
        y0=lineSegments[1]
        y1=lineSegments[3]
        
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    x, y = x0, y0
    sx = -1 if x0 > x1 else 1
    sy = -1 if y0 > y1 else 1

    if dx > dy:
        err = dx / 2.0
        #print("aaa")

        while x <= x1:
            polypoint2D([x,y],color)
            err -= dy
            if err < 0:
                y += sy
                err += dx
            x += sx
    else:
        y=int(y0)
        err = dy / 2.0
        while int(y) != int(y1):
            polypoint2D([x,y],color)
            err -= dx
            if err < 0:
                x += sx
                err += dy
            y += sy 
    
    polypoint2D([x,y],color)
        
    #print("/////////////////")


    x = gpu.GPU.width//2
    y = gpu.GPU.height//2

def triangleSet2D(vertices, color):
    """ Função usada para renderizar TriangleSet2D. """

    len_color = len(color) # Usado para ver se vai interpolar ou não
    
    x0=vertices[0] # xa
    y0=vertices[1] # ya
    x1=vertices[2] # xb
    y1=vertices[3] # yb
    x2=vertices[4] # xc
    y2=vertices[5] # yc

    Xl=[x0,x1,x2]
    Xl=sorted(Xl)
    Yl=[y0,y1,y2]
    Yl=sorted(Yl)


    N0=[y1-y0,-(x1-x0)]
    N1=[y2-y1,-(x2-x1)]
    N2=[y0-y2,-(x0-x2)]



    for x in range(int(Xl[0]),int(Xl[2])):
        for y in range(int(Yl[0]),int(Yl[2])+1):

            V0=[x-x0,y-y0]
            V1=[x-x1,y-y1]
            V2=[x-x2,y-y2]

            L0=V0[0]*N0[0]+V0[1]*N0[1]
            L1=V1[0]*N1[0]+V1[1]*N1[1]
            L2=V2[0]*N2[0]+V2[1]*N2[1]

            if(L0>0 and L1>0 and L2>0):
                if len_color == 3:
                    polypoint2D([x,y],color)
                elif len_color == 9:
                    alpha = (-(x-x1)*(y2-y1) + (y-y1)*(x2-x1)) / (-(x0-x1)*(y2-y1) + (y0-y1)*(x2-x1))
                    beta = (-(x-x2)*(y0-y2) + (y-y2)*(x0-x2)) / (-(x1-x2)*(y0-y2) + (y1-y2)*(x0-x2))
                    gamma = 1 - alpha - beta
                    #print("alpha: {}; beta: {}; gamma: {}".format(alpha, beta, gamma))
                    A = [x * alpha for x in color[0:3]]
                    B = [x * beta for x in color[3:6]]
                    C = [x * gamma for x in color[6:9]]
                    
                    
                    colorInterpol = [sum(x) for x in zip(A, B, C)]
                    polypoint2D([x,y],colorInterpol)
                else:
                    raise ValueError("Array 'color' de tamanho {}".format(len_color))
                


def triangleSet(point, color):
    # 2o 
    """ Função usada para renderizar TriangleSet. """
    # Nessa função você receberá pontos no parâmetro point, esses pontos são uma lista
    # de pontos x, y, e z sempre na ordem. Assim point[0] é o valor da coordenada x do
    # primeiro ponto, point[1] o valor y do primeiro ponto, point[2] o valor z da 
    # coordenada z do primeiro ponto. Já point[3] é a coordenada x do segundo ponto e
    # assim por diante.
    # No TriangleSet os triângulos são informados individualmente, assim os três
    # primeiros pontos definem um triângulo, os três próximos pontos definem um novo
    # triângulo, e assim por diante.
    
    # O print abaixo é só para vocês verificarem o funcionamento, deve ser removido.


    i = 0
    while i < len(point):
        p1 = np.array(point[i:i+3]+[1]).T
        p2 = np.array(point[i+3:i+6]+[1]).T
        p3 = np.array(point[i+6:i+9]+[1]).T

        new_p1 = np.dot(TRANSFORM_STACK[-1], p1)
        new_p2 = np.dot(TRANSFORM_STACK[-1], p2)
        new_p3 = np.dot(TRANSFORM_STACK[-1], p3)


        transform_triangle_matrix = np.array([new_p1, new_p2, new_p3]).T

        norm_triangle_matrix = norm_array_from_matrix(transform_triangle_matrix)

        coord_x_norm = np.dot(COORDENADAS_TELA, norm_triangle_matrix).T


        vertices = np.concatenate((coord_x_norm[0][0:2],coord_x_norm[1][0:2],coord_x_norm[2][0:2]), axis=None)
        #print("Vertices")
        #print(vertices)
        triangleSet2D(vertices, color)

        
        i += 9


def viewpoint(position, orientation, fieldOfView):
    # 1o
    """ Função usada para renderizar (na verdade coletar os dados) de Viewpoint. """
    #print("Viewpoint : position = {0}, orientation = {1}, fieldOfView = {2}".format(position, orientation, fieldOfView)) # imprime no terminal
    
    
    if orientation[0]:
        orientation_matrix = np.array([[1, 0, 0, 0],
                                    [0, cos(orientation[3]), -sin(orientation[3]), 0],
                                    [0, sin(orientation[3]), cos(orientation[3]), 0],
                                    [0, 0, 0, 1]])
    elif orientation[1]:
        orientation_matrix = np.array([[cos(orientation[3]), 0, sin(orientation[3]), 0],
                                    [0, 1, 0, 0],
                                    [-sin(orientation[3]), 0, cos(orientation[3]), 0],
                                    [0, 0, 0, 1]])
    elif orientation[2]:
        orientation_matrix = np.array([[cos(orientation[3]), -sin(orientation[3]), 0, 0],
                                    [sin(orientation[3]), cos(orientation[3]), 0, 0],
                                    [0, 0, 1, 0],
                                    [0, 0, 0, 1]])


                                    
    
    position_matrix = np.array([[1, 0, 0, -position[0]],
                                   [0, 1, 0, -position[1]],
                                   [0, 0, 1, -position[2]],
                                   [0, 0, 0, 1]])

    look_at_matrix = np.dot(orientation_matrix, position_matrix)


  

    aspect = LARGURA/ALTURA
    near = 0.5
    far = 100

    top = near * tan(fieldOfView)
    bottom = -top
    right = top*aspect
    left = -right



    perspective_matrix = np.array([[near/right, 0, 0, 0],
                                  [0, near/top, 0, 0],
                                  [0, 0, -(far+near)/(far-near), -(2*far*near)/(far-near)],
                                  [0, 0, -1, 0]])


    TRANSFORM_STACK.append(np.dot(look_at_matrix, TRANSFORM_STACK[-1]))
    TRANSFORM_STACK.append(np.dot(perspective_matrix, TRANSFORM_STACK[-1]))



def transform(translation, scale, rotation):
    # 1o
    """ Função usada para renderizar (na verdade coletar os dados) de Transform. """
    # A função transform será chamada quando se entrar em um nó X3D do tipo Transform
    # do grafo de cena. Os valores passados são a escala em um vetor [x, y, z]
    # indicando a escala em cada direção, a translação [x, y, z] nas respectivas
    # coordenadas e finalmente a rotação por [x, y, z, t] sendo definida pela rotação
    # do objeto ao redor do eixo x, y, z por t radianos, seguindo a regra da mão direita.
    # Quando se entrar em um nó transform se deverá salvar a matriz de transformação dos
    # modelos do mundo em alguma estrutura de pilha.

    # O print abaixo é só para vocês verificarem o funcionamento, deve ser removido.
    #print("Transform : t: {} ; s: {} ; r: {}".format(translation, scale, rotation), end= "")
    
    translation_matrix = np.array([[1, 0, 0, translation[0]],
                                       [0, 1, 0, translation[1]],
                                       [0, 0, 1, translation[2]],
                                       [0, 0, 0, 1]])
    scale_matrix = np.array([[scale[0], 0, 0, 0],
                                 [0, scale[1], 0, 0],
                                 [0, 0, scale[2], 0],
                                 [0, 0, 0, 1]])
    angle = rotation[3]
    if rotation[0]:
        rotation_matrix = np.array([[1, 0, 0, 0],
                                [0, cos(angle), -sin(angle), 0],
                                [0, sin(angle), cos(angle), 0],
                                [0, 0, 0, 1]])
    elif rotation[1]:
        rotation_matrix = np.array([[cos(angle), 0, sin(angle), 0],
                                [0, 1, 0, 0],
                                [-sin(angle), 0, cos(angle), 0],
                                [0, 0, 0, 1]])
    elif rotation[2]:
        rotation_matrix = np.array([[cos(angle), -sin(angle), 0, 0],
                                [sin(angle), cos(angle), 0, 0],
                                [0, 0, 1 ,0],
                                [0, 0, 0, 1]])

    m1 = np.dot(translation_matrix, scale_matrix)
    m2 = np.dot(m1, rotation_matrix)
    TRANSFORM_STACK.append(np.dot(TRANSFORM_STACK[-1], m2))


def _transform():
    """ Função usada para renderizar (na verdade coletar os dados) de Transform. """
    # A função _transform será chamada quando se sair em um nó X3D do tipo Transform do
    # grafo de cena. Não são passados valores, porém quando se sai de um nó transform se
    # deverá recuperar a matriz de transformação dos modelos do mundo da estrutura de
    # pilha implementada.
    #print("Saindo de Transform. Len stack: {}".format(len(TRANSFORM_STACK)))
    #print(len(TRANSFORM_STACK))

    TRANSFORM_STACK.pop()
    
    # O print abaixo é só para vocês verificarem o funcionamento, deve ser removido.
    

def triangleStripSet(point, stripCount, color):
    """ Função usada para renderizar TriangleStripSet. """
    #print("TriangleStripSet : pontos = {0} ".format(point), end = '')

    point_index=0
    for _ in range(int(stripCount[0]-2)):
        point1=point[point_index:point_index+3]
        point2=point[point_index+3:point_index+6]
        point3=point[point_index+6:point_index+9]
        
        if(point_index%2==0):
            pointList=point1+point2+point3
        else:
            pointList=point2+point1+point3

        point_index+=3
        triangleSet(pointList,color)


    # A função triangleStripSet é usada para desenhar tiras de triângulos interconectados,
    # você receberá as coordenadas dos pontos no parâmetro point, esses pontos são uma
    # lista de pontos x, y, e z sempre na ordem. Assim point[0] é o valor da coordenada x
    # do primeiro ponto, point[1] o valor y do primeiro ponto, point[2] o valor z da
    # coordenada z do primeiro ponto. Já point[3] é a coordenada x do segundo ponto e assim
    # por diante. No TriangleStripSet a quantidade de vértices a serem usados é informado
    # em uma lista chamada stripCount (perceba que é uma lista).
    #print(stripCount)

    # O print abaixo é só para vocês verificarem o funcionamento, deve ser removido.
     # imprime no terminal pontos
    #for i, strip in enumerate(stripCount):
    #    pass
    #    print("strip[{0}] = {1} ".format(i, strip), end = '') # imprime no terminal
    #print("")

def indexedTriangleStripSet(point, index, color):
    """ Função usada para renderizar IndexedTriangleStripSet. """
    # A função indexedTriangleStripSet é usada para desenhar tiras de triângulos
    # interconectados, você receberá as coordenadas dos pontos no parâmetro point, esses
    # pontos são uma lista de pontos x, y, e z sempre na ordem. Assim point[0] é o valor
    # da coordenada x do primeiro ponto, point[1] o valor y do primeiro ponto, point[2]
    # o valor z da coordenada z do primeiro ponto. Já point[3] é a coordenada x do
    # segundo ponto e assim por diante. No IndexedTriangleStripSet uma lista informando
    # como conectar os vértices é informada em index, o valor -1 indica que a lista
    # acabou. A ordem de conexão será de 3 em 3 pulando um índice. Por exemplo: o
    # primeiro triângulo será com os vértices 0, 1 e 2, depois serão os vértices 1, 2 e 3,
    # depois 2, 3 e 4, e assim por diante.
    
    # O print abaixo é só para vocês verificarem o funcionamento, deve ser removido.
    #print("IndexedTriangleStripSet : pontos = {0}, index = {1}".format(point, index)) # imprime no terminal pontos
    #0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, -1.0

    dict_point = {}

    for i in range(len(index)-1):
        dict_point[i] = point[3*i:3*(i+1)]


    for i in range(len(index)-3):
        point1 = dict_point[index[i]]
        point2 = dict_point[index[i+1]]
        point3 = dict_point[index[i+2]]

        if(i%2==0):
            pointList=point1+point2+point3
        else:
            pointList=point2+point1+point3

        triangleSet(pointList,color)

def box(size, color):
    """ Função usada para renderizar Boxes. """
    # A função box é usada para desenhar paralelepípedos na cena. O Box é centrada no
    # (0, 0, 0)  no sistema de coordenadas local e alinhado com os eixos de coordenadas
    # locais. O argumento size especifica as extensões da caixa ao longo dos eixos X, Y
    # e Z, respectivamente, e cada valor do tamanho deve ser maior que zero. Para desenha
    # essa caixa você vai provavelmente querer tesselar ela em triângulos, para isso
    # encontre os vértices e defina os triângulos.

    # O print abaixo é só para vocês verificarem o funcionamento, deve ser removido.
    #print("Box : size = {0}".format(size)) # imprime no terminal pontos
    # 8 pontos
    # 12 triangulos

    ps = {}

    x = size[0]/2
    y = size[1]/2
    z = size[2]/2

    #size = 1

    ps[0] = [-x, y, z]
    ps[1] = [-x, -y, z]
    ps[2] = [x, y, z]
    ps[3] = [x, -y, z]
    ps[4] = [x, y, -z]
    ps[5] = [x, -y, -z]
    ps[6] = [-x, y, -z]
    ps[7] = [-x, -y, -z]

    triangleStripSet(ps[0]+ps[1]+ps[2]+ps[3], [4], color)
    triangleStripSet(ps[2]+ps[3]+ps[4]+ps[5], [4], color)
    triangleStripSet(ps[4]+ps[5]+ps[6]+ps[7], [4], color)
    triangleStripSet(ps[6]+ps[7]+ps[0]+ps[1], [4], color)
    triangleStripSet(ps[6]+ps[0]+ps[4]+ps[2], [4], color)
    triangleStripSet(ps[1]+ps[7]+ps[3]+ps[5], [4], color)
    
def indexedFaceSet(coord, coordIndex, colorPerVertex, color, colorIndex, texCoord, texCoordIndex, current_color, current_texture):
    """ Função usada para renderizar IndexedFaceSet. """
    # A função indexedFaceSet é usada para desenhar malhas de triângulos. Ela funciona de
    # forma muito simular a IndexedTriangleStripSet porém com mais recursos.
    # Você receberá as coordenadas dos pontos no parâmetro cord, esses
    # pontos são uma lista de pontos x, y, e z sempre na ordem. Assim point[0] é o valor
    # da coordenada x do primeiro ponto, point[1] o valor y do primeiro ponto, point[2]
    # o valor z da coordenada z do primeiro ponto. Já point[3] é a coordenada x do
    # segundo ponto e assim por diante. No IndexedFaceSet uma lista informando
    # como conectar os vértices é informada em coordIndex, o valor -1 indica que a lista
    # acabou. A ordem de conexão será de 3 em 3 pulando um índice. Por exemplo: o
    # primeiro triângulo será com os vértices 0, 1 e 2, depois serão os vértices 1, 2 e 3,
    # depois 2, 3 e 4, e assim por diante.
    # Adicionalmente essa implementação do IndexedFace suport cores por vértices, assim
    # a se a flag colorPerVertex estiver habilidades, os vértices também possuirão cores
    # que servem para definir a cor interna dos poligonos, para isso faça um cálculo
    # baricêntrico de que cor deverá ter aquela posição. Da mesma forma se pode definir uma
    # textura para o poligono, para isso, use as coordenadas de textura e depois aplique a
    # cor da textura conforme a posição do mapeamento. Dentro da classe GPU já está
    # implementadado um método para a leitura de imagens.
    
    # O print abaixo é só para vocês verificarem o funcionamento, deve ser removido.

    #print(coord)
    #print(current_color)
    #print(texCoord)
    #print("colorPerVertex: {}\ncolor: {}\ncolorIndex: {}".format(colorPerVertex, color, colorIndex))
    print("texCoord: {}\ntexCoordIndex: {}\ncurrent_texture: {}".format(texCoord, texCoordIndex, current_texture))
    for i in range(0,len(coordIndex)-2,4):
        p1=coordIndex[i]
        p2=coordIndex[i+1]
        p3=coordIndex[i+2]
        point1=coord[3*p1:3*(p1+1)]
        point2=coord[3*p2:3*(p2+1)]
        point3=coord[3*p3:3*(p3+1)]
        pointList=point1+point2+point3
        
        if colorPerVertex: # interpolação de cores
            # Faz a msm coisa dos pontos, só que com as cores.
            ### Pega o colorIndex (coordIndex) e o color (point) e faz uma lista ...
            ### ... das cores de cada ponto (equivalente ao pointList)
            c1=colorIndex[i]
            c2=colorIndex[i+1]
            c3=colorIndex[i+2]
            color1=color[3*c1:3*(c1+1)]
            color2=color[3*c2:3*(c2+1)]
            color3=color[3*c3:3*(c3+1)]

            colorList = color1+color2+color3
            triangleSet(pointList, colorList)
        else:
            triangleSet(pointList,current_color)



# Defina o tamanhã da tela que melhor sirva para perceber a renderização
LARGURA = 400
ALTURA = 200
if __name__ == '__main__':

    # Valores padrão da aplicação
    width = LARGURA
    height = ALTURA
    x3d_file = "exemplo8.x3d"
    image_file="insper.png"

    # Tratando entrada de parâmetro
    parser = argparse.ArgumentParser(add_help=False)   # parser para linha de comando
    parser.add_argument("-i", "--input", help="arquivo X3D de entrada")
    parser.add_argument("-o", "--output", help="arquivo 2D de saída (imagem)")
    parser.add_argument("-w", "--width", help="resolução horizonta", type=int)
    parser.add_argument("-h", "--height", help="resolução vertical", type=int)
    parser.add_argument("-q", "--quiet", help="não exibe janela de visualização", action='store_true')
    args = parser.parse_args() # parse the arguments
    if args.input: x3d_file = args.input
    if args.output: image_file = args.output
    if args.width: width = args.width
    if args.height: height = args.height

    # Iniciando simulação de GPU
    gpu.GPU(width, height, image_file)

    # Abre arquivo X3D
    scene = x3d.X3D(x3d_file)
    scene.set_resolution(width, height)

    # funções que irão fazer o rendering
    x3d.X3D.render["Polypoint2D"] = polypoint2D
    x3d.X3D.render["Polyline2D"] = polyline2D
    x3d.X3D.render["TriangleSet2D"] = triangleSet2D
    x3d.X3D.render["TriangleSet"] = triangleSet
    x3d.X3D.render["Viewpoint"] = viewpoint
    x3d.X3D.render["Transform"] = transform
    x3d.X3D.render["_Transform"] = _transform
    x3d.X3D.render["TriangleStripSet"] = triangleStripSet
    x3d.X3D.render["IndexedTriangleStripSet"] = indexedTriangleStripSet
    x3d.X3D.render["Box"] = box
    x3d.X3D.render["IndexedFaceSet"] = indexedFaceSet

    # Se no modo silencioso não configurar janela de visualização
    if not args.quiet:
        window = interface.Interface(width, height)
        scene.set_preview(window)

    scene.parse() # faz o traversal no grafo de cena

    # Se no modo silencioso salvar imagem e não mostrar janela de visualização
    if args.quiet:
        gpu.GPU.save_image() # Salva imagem em arquivo
    else:
        window.image_saver = gpu.GPU.save_image # pasa a função para salvar imagens
        window.preview(gpu.GPU._frame_buffer) # mostra janela de visualização

    '''
    for m in TRANSFORM_STACK:
        print(m)
        print("")
    '''