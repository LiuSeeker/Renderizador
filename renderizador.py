# Desenvolvido por: Luciano Soares <lpsoares@insper.edu.br>
# Disciplina: Computação Gráfica
# Data: 28 de Agosto de 2020

import argparse     # Para tratar os parâmetros da linha de comando
import x3d          # Faz a leitura do arquivo X3D, gera o grafo de cena e faz traversal
import interface    # Janela de visualização baseada no Matplotlib
import gpu          # Simula os recursos de uma GPU

import numpy as np
from math import sin, cos

TRANSFORM_STACK = []

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
        for k in range(n_points):
            gpu.GPU.set_pixel(int(point[i]), int(point[i+1]), int(255/n_points), 0, 0)
            if split_h:
                gpu.GPU.set_pixel(int(point[i])-1, int(point[i+1]), int(255/n_points), 0, 0)
            if split_v:
                gpu.GPU.set_pixel(int(point[i]), int(point[i+1])-1, int(255/n_points), 0, 0)
            if split_h and split_v:
                gpu.GPU.set_pixel(int(point[i])-1, int(point[i+1])-1, int(255/n_points), 0, 0)
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
        
    #print(x0,y0)
    #print(x1,y1)


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
    
    x0=vertices[0]
    y0=vertices[1]
    x1=vertices[2]
    y1=vertices[3]
    x2=vertices[4]
    y2=vertices[5]

    #print(x0,y0)
    #print(x1,y1)
    #print(x2,y2)



    Xl=[x0,x1,x2]
    Xl=sorted(Xl)
    Yl=[y0,y1,y2]
    Yl=sorted(Yl)

    linha0=[x1-x0,y1-y0]
    linha1=[x2-x1,y2-y1]
    linha2=[x0-x2,y0-y2]
    #print(linha0)


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
                polypoint2D([x,y],color)

    #print("/////////////////")


def triangleSet(point, color):
    # 2o 
    """ Função usada para renderizar TriangleSet. """
    print("TriangleSet : pontos = {0}".format(point)) # imprime no terminal pontos

def viewpoint(position, orientation, fieldOfView):
    # 1o
    """ Função usada para renderizar (na verdade coletar os dados) de Viewpoint. """
    print("Viewpoint : position = {0}, orientation = {1}, fieldOfView = {2}".format(position, orientation, fieldOfView)) # imprime no terminal

def transform(translation, scale, rotation):
    # 1o
    """ Função usada para renderizar (na verdade coletar os dados) de Transform. """
    #print("Transform : ", end = '')
    print("Transform call ", end="")
    
    if translation != [0,0,0]:
        print("translation")
        #print("translation = {0} ".format(translation), end = '') # imprime no terminal
        translation_matrix = np.array([[1, 0, 0, translation[0]],
                                       [0, 1, 0, translation[1]],
                                       [0, 0, 1, translation[2]],
                                       [0, 0, 0, 1]])
        TRANSFORM_STACK.append(translation_matrix)
        

    if scale != [1,1,1]:
        print("scale")
        #print("scale = {0} ".format(scale), end = '') # imprime no terminal
        scale_matrix = np.array([[scale[0], 0, 0, 0],
                                 [0, scale[1], 0, 0],
                                 [0, 0, scale[2], 0],
                                 [0, 0, 0, 1]])
        TRANSFORM_STACK.append(scale_matrix)

    if rotation != [0,0,1,0]:
        print("rotation")
        angle = rotation[3]
        #print("rotation = {0} ".format(rotation), end = '') # imprime no terminal
        if rotation[0]:
            rotation_matrix = np.array([[1, 0, 0],
                                       [0, cos(angle), -sin(angle)],
                                       [0, sin(angle), cos(angle)]])
        elif rotation[1]:
            rotation_matrix = np.array([[cos(angle), 0, sin(angle)],
                                       [0, 1, 0],
                                       [-sin(angle), 0, cos(angle)]])
        elif rotation[2]:
            rotation_matrix = np.array([[cos(angle), -sin(angle), 0],
                                       [sin(angle), cos(angle), 0],
                                       [0, 0, 1]])
        TRANSFORM_STACK.append(rotation_matrix)

    print("")

def triangleStripSet(point, stripCount, color):
    """ Função usada para renderizar TriangleStripSet. """
    print("TriangleStripSet : pontos = {0} ".format(point), end = '') # imprime no terminal pontos
    for i, strip in enumerate(stripCount):
        print("strip[{0}] = {1} ".format(i, strip), end = '') # imprime no terminal
    print("")

def indexedTriangleStripSet(point, index, color):
    """ Função usada para renderizar IndexedTriangleStripSet. """
    print("IndexedTriangleStripSet : pontos = {0}, index = {1}".format(point, index)) # imprime no terminal pontos

def box(size, color):
    """ Função usada para renderizar Boxes. """
    print("Box : size = {0}".format(size)) # imprime no terminal pontos


LARGURA = 30
ALTURA = 20

   

if __name__ == '__main__':

    # Valores padrão da aplicação
    width = LARGURA
    height = ALTURA

    x3d_file = "exemplo4.x3d"
    image_file = "tela.png"

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
    x3d.X3D.render["TriangleStripSet"] = triangleStripSet
    x3d.X3D.render["IndexedTriangleStripSet"] = indexedTriangleStripSet
    x3d.X3D.render["Box"] = box

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

    for m in TRANSFORM_STACK:
        print(m)
        print("")