# Nombres
 - Nicolas Gonzalez 202310041.
 - Samuel Rodríguez 202310140.
 - Mauricio Martinez 202314461

 # Proyecto – Metaheurística (GA) para Ruteo Urbano

Este proyecto implementa un algoritmo genético (GA) para resolver un problema de ruteo de vehículos en un contexto urbano.  
Se incluyen tres instancias del problema:

- **Caso base** (`Proyecto_Caso_Base`)
- **Caso 2** (`Proyecto_Caso_2`)
- **Caso 3** (`Proyecto_Caso_3`)

Cada caso tiene su propio notebook de ejecución, pero comparten la misma estructura de código en `src/`.

---

## Dependencias y requisitos

- Librerías utilizadas:
  - `numpy`
  - `pandas`
  - `matplotlib`
  - `folium`
  - `jupyter` o soporte de notebooks en VS Code.

La ejecución principal se realiza a través de los notebooks ubicados en `src/`, uno por cada instancia del problema.

### 3.1. Caso base

1. Abrir `src/main_Caso_Base.ipynb`.
2. Verificar la ruta del caso:
3. Ejecutar las celdas en orden:
- Carga de datos y parámetros.
- Definición de parámetros del GA.
- Ejecución del GA con **3 semillas** distintas.
- Selección de la mejor solución.
- Exportación del archivo de verificación.
- Generación del gráfico de convergencia.
- Generación del mapa de rutas con `folium`.

Ejecutar el mismo procedimiento para caso 2 y 3 en su archivo jupyter correspondiente




