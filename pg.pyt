
buttons = [ "Control de Efectivo", "Reporte de ventas", "ReImpresión", 
            "Retiro de Efectivo", "Nivel de Cambio", "Usuarios",
            "Retiro total de valores", "Apertura de servicio", "Salir"
            ]

positions = [(i,j) for i in range(3) for j in range(3)]
for pos, text in zip(positions, buttons):
    print(*pos, text)