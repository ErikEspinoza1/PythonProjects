import requests
import xml.etree.ElementTree as ET

def obtener_datos_bce():
    """
    Se conecta al BCE, descarga el XML y extrae la fecha y las tasas.
    Retorna: (fecha, diccionario_tasas)
    """
    url = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"
    
    try:
        # 1. Petición HTTP (GET) [cite: 8, 16]
        response = requests.get(url)
        
        if response.status_code == 200:
            # 2. Parsing del XML [cite: 9, 49]
            root = ET.fromstring(response.content)
            namespaces = {'gesmes': 'http://www.gesmes.org/xml/2002-08-01', 
                          'ecb': 'http://www.ecb.int/vocabulary/2002-08-01/eurofxref'}
            data_cube = root.find('.//ecb:Cube/ecb:Cube', namespaces)
            fecha = data_cube.attrib.get('time')
            tasas = {'EUR': 1.0}

            for currency_node in data_cube:
                moneda = currency_node.attrib.get('currency')
                tasa = currency_node.attrib.get('rate')
                
                if moneda and tasa:
                    tasas[moneda] = float(tasa)
            
            return fecha, tasas
            
        else:
            print("Error al conectar con el servidor.")
            return None, None

    except Exception as e:
        print(f"Ha ocurrido un error: {e}")
        return None, None

def calcular_conversion(cantidad, moneda_origen, moneda_destino, tasas):
    """
    Realiza la conversión cruzada usando el Euro como puente.
    Fórmula: (Cantidad / TasaOrigen) * TasaDestino [cite: 70, 71, 72]
    """
    try:
        tasa_origen = tasas[moneda_origen]
        tasa_destino = tasas[moneda_destino]
        
        # Lógica matemática [cite: 81]
        resultado = (cantidad / tasa_origen) * tasa_destino
        return resultado
    except KeyError:
        return None

if __name__ == "__main__":
    print("Probando descarga de datos...")
    fecha_actual, mis_tasas = obtener_datos_bce()
    
    if mis_tasas:
        print(f"Datos cargados con éxito. Fecha: {fecha_actual}")
        print(f"Total monedas encontradas: {len(mis_tasas)}")
        print("Ejemplo de tasas:", list(mis_tasas.items())[:5])
        
        # Prueba de conversión
        test_cant = 100
        res = calcular_conversion(test_cant, 'EUR', 'USD', mis_tasas)
        print(f"\nPrueba: {test_cant} EUR son {res:.2f} USD")
    else:
        print("Falló la descarga.")