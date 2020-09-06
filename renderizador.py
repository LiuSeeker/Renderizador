# Desenvolvido por: Luciano Soares
# Displina: Computação Gráfica
# Data: 28 de Agosto de 2020

import argparse

# X3D
import x3d

# Interface
import interface

# GPU
import gpu

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
        
    print(x0,y0)
    print(x1,y1)

    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    x, y = x0, y0
    sx = -1 if x0 > x1 else 1
    sy = -1 if y0 > y1 else 1

    if dx > dy:
        err = dx / 2.0
        print("aaa")
        while x <= x1:
            polypoint2D([x,y],color)
            err -= dy
            if err < 0:
                y += sy
                err += dx
            x += sx
    else:
        print("bb")
        err = dy / 2.0
        while int(y) != int(y1):
            polypoint2D([x,y],color)
            err -= dx
            if err < 0:
                x += sx
                err += dy
            y += sy 
    
    polypoint2D([x,y],color)
        
    print("/////////////////")

    x = gpu.GPU.width//2
    y = gpu.GPU.height//2

def triangleSet2D(vertices, color):
    """ Função usada para renderizar TriangleSet2D. """
    gpu.GPU.set_pixel(24, 8, 255, 255, 0) # altera um pixel da imagem

LARGURA = 30
ALTURA = 20

if __name__ == '__main__':
    
    width = LARGURA
    height = ALTURA
    x3d_file = "exemplo2.x3d"
    image_file = "tela.png"

    # Tratando entrada de parâmetro
    parser = argparse.ArgumentParser(add_help=False)   # parser para linha de comando
    parser.add_argument("-i", "--input", help="arquivo X3D de entrada")
    parser.add_argument("-o", "--output", help="arquivo 2D de saída (imagem)")
    parser.add_argument("-w", "--width", help="resolução horizonta", type=int)
    parser.add_argument("-h", "--height", help="resolução vertical", type=int)
    args = parser.parse_args() # parse the arguments
    if args.input: x3d_file = args.input
    if args.output: image_file = args.output
    if args.width: width = args.width
    if args.height: height = args.height
    
    # Iniciando simulação de GPU
    gpu.GPU(width, height)

    # Abre arquivo X3D
    scene = x3d.X3D(x3d_file)
    scene.set_resolution(width, height)

    # funções que irão fazer o rendering
    x3d.X3D.render["Polypoint2D"] = polypoint2D
    x3d.X3D.render["Polyline2D"] = polyline2D
    x3d.X3D.render["TriangleSet2D"] = triangleSet2D

    scene.parse() # faz o traversal no grafo de cena
    interface.Interface(width, height, image_file).preview(gpu.GPU._frame_buffer)
