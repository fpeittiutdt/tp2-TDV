import json
import networkx as nx
import matplotlib.pyplot as plt
import main_combinado as gr


def main():
	filename = "instances/toy_instance.json"
	#filename = "instances/retiro-tigre-semana.json"
	#filename = "instances/retiro-tigre-reducido.json"

	with open(filename) as json_file:
		data = json.load(json_file)

	# test file reading

	for service in data["services"]:
		print(service, data["services"][service]["stops"])
	
	grafo_retiro_tigre, posiciones, night_edges = gr.create_graph(data)

	lista_retiro = []
	lista_tigre = []
	lista_colores = []
	labels = {}
	for nodo in grafo_retiro_tigre.nodes(data=True):
		lista_colores.append(nodo[1]["color"])
		labels[nodo[0]] = nodo[0]
		if nodo[1]["stations"] == "Retiro":
			lista_retiro.append(nodo[0])
		else:
			lista_tigre.append(nodo[0])
	
	lista_tigre.sort()
	lista_retiro.sort()
	
	#pos = nx.bipartite_layout(grafo_retiro_tigre, nodes=lista_retiro)

	nx.draw_networkx_nodes(
        grafo_retiro_tigre,
        node_color=lista_colores,
        pos=posiciones,
        node_size=400,
        node_shape="s",
        linewidths=grafo_retiro_tigre.number_of_nodes() * [1],
    )
	
	nx.draw_networkx_labels(
        grafo_retiro_tigre, pos=posiciones, labels=labels, font_size=8, font_family="serif"
    )

	i = 0
	for edge in grafo_retiro_tigre.edges():
		if edge in night_edges:
			nx.draw_networkx_edges(
                grafo_retiro_tigre,
                pos=posiciones,
                edgelist=[edge],
                connectionstyle="arc3, rad = 0.5",
            )
		else:
			nx.draw_networkx_edges(
                grafo_retiro_tigre, edgelist=[edge], pos=posiciones
            )
		i += 1

	plt.gca().invert_yaxis()
	plt.gca().invert_xaxis()
	plt.show()

	"""for arista in grafo_retiro_tigre.edges():
		if (arista[0] == lista_retiro[0] and arista[1] == lista_retiro[len(lista_retiro)-1]) or (arista[0] == lista_tigre[len(lista_tigre)-1] and arista[1] == lista_tigre[0]):
			nx.draw_networkx_edges(grafo_retiro_tigre, edgelist=[arista], pos=pos, connectionstyle="arc3, rad = 0.5")
		else:
			nx.draw_networkx_edges(grafo_retiro_tigre, edgelist=[arista], pos=pos)

	nx.draw(grafo_retiro_tigre, pos, with_labels = True, font_weight ="bold", node_color=[nodo[1]["color"] for nodo in grafo_retiro_tigre.nodes(data=True)], node_size = 1000)
	labels = nx.get_edge_attributes(grafo_retiro_tigre, "upper_bound")
	nx.draw_networkx_edge_labels(grafo_retiro_tigre, pos, edge_labels=labels)
	plt.show()"""

	solucion = nx.min_cost_flow(grafo_retiro_tigre, capacity="upper_bound")
	costo_minimo = nx.cost_of_flow(grafo_retiro_tigre, solucion)
	print("solucion: ", solucion, "costo minimo: ", costo_minimo)

	for nodo1 in solucion:
		for nodo2 in solucion[nodo1]:
			solucion[nodo1][nodo2] += grafo_retiro_tigre[nodo1][nodo2]["amount_modified"]
	
	print("solucion modificada: ", solucion)

	flujo_retiro = solucion[lista_retiro[0]][lista_retiro[len(lista_retiro)-1]]
	flujo_tigre = solucion[lista_tigre[len(lista_tigre)-1]][lista_tigre[0]]
	primero_retiro = (lista_retiro[0], flujo_retiro)
	primero_tigre = (lista_tigre[len(lista_tigre)-1], flujo_tigre)

	print("retiro: ", primero_retiro, "tigre: ", primero_tigre)

	costo_minimo = nx.cost_of_flow(grafo_retiro_tigre, solucion)
	print("costo minimo: ", costo_minimo)


	print("AGREGANDO MODIFICACION")

	nuevo_grafo = gr.agregar_limitacion(grafo_retiro_tigre, "Tigre", 10)

	lista_retiro = []
	lista_tigre = []
	for nodo in nuevo_grafo.nodes(data=True):
		if nodo[1]["stations"] == "Retiro":
			lista_retiro.append(nodo[0])
		else:
			lista_tigre.append(nodo[0])
	
	lista_tigre.sort()
	lista_retiro.sort(reverse=True)
	pos = nx.spring_layout(nuevo_grafo)
	nx.draw(nuevo_grafo, pos, with_labels = True, font_weight ="bold", node_color=[nodo[1]["color"] for nodo in nuevo_grafo.nodes(data=True)], node_size = 1000)
	labels = nx.get_edge_attributes(nuevo_grafo, "upper_bound")
	nx.draw_networkx_edge_labels(nuevo_grafo, pos, edge_labels=labels)
	plt.show()

	solucion = nx.min_cost_flow(nuevo_grafo, capacity="upper_bound")

	print("solucion: ", solucion)

	for nodo1 in solucion:
		for nodo2 in solucion[nodo1]:
			solucion[nodo1][nodo2] += nuevo_grafo[nodo1][nodo2]["amount_modified"]
	
	print("solucion modificada: ", solucion)

	primero_retiro = (lista_retiro[len(lista_retiro)-1], None)
	primero_tigre = (lista_tigre[0], None)
	for nodo in solucion:
		if nodo == primero_retiro[0]:
			flujo_retiro = 0
			for vecino in solucion[nodo]:
				flujo_retiro += solucion[nodo][vecino]
			primero_retiro = (primero_retiro[0], flujo_retiro)
		elif nodo == primero_tigre[0]:
			flujo_tigre = 0
			for vecino in solucion[nodo]:
				flujo_tigre += solucion[nodo][vecino]
			primero_tigre = (primero_tigre[0], flujo_tigre)

	print("retiro: ", primero_retiro, "tigre: ", primero_tigre)

if __name__ == "__main__":
	main()