from flask import jsonify, request
from src.config.db import session
from src.models.coche import Coche

def init_api_routes(app):

    # 1. CREATE (POST): Crear un nuevo coche
    @app.route('/api/coche', methods=['POST'])
    def create_coche():
        data = request.get_json()
        nuevo_coche = Coche(
            marca=data['marca'],
            modelo=data['modelo'],
            anyo=data['anyo'],
            precio=data['precio']
        )
        session.add(nuevo_coche)
        session.commit()
        return jsonify({"mensaje": "Coche creado", "id": nuevo_coche.id}), 201

    # 2. RETRIEVE (GET): Obtener todos los coches
    @app.route('/api/coche', methods=['GET'])
    def get_coches():
        coches = session.query(Coche).all()
        lista_coches = []
        for c in coches:
            lista_coches.append({
                'id': c.id,
                'marca': c.marca,
                'modelo': c.modelo,
                'anyo': c.anyo,
                'precio': c.precio
            })
        return jsonify(lista_coches), 200

    # 3. RETRIEVE ONE (GET): Obtener un coche por su ID
    @app.route('/api/coche/<id>', methods=['GET'])
    def get_coche_by_id(id):
        coche = session.query(Coche).filter_by(id=id).first()
        if coche:
            return jsonify({
                'id': coche.id,
                'marca': coche.marca,
                'modelo': coche.modelo,
                'anyo': coche.anyo,
                'precio': coche.precio
            }), 200
        return jsonify({"error": "Coche no encontrado"}), 404

    # 4. UPDATE (PUT): Actualizar un coche existente
    @app.route('/api/coche/<id>', methods=['PUT'])
    def update_coche(id):
        data = request.get_json()
        coche = session.query(Coche).filter_by(id=id).first()
        
        if coche:
            coche.marca = data.get('marca', coche.marca)
            coche.modelo = data.get('modelo', coche.modelo)
            coche.anyo = data.get('anyo', coche.anyo)
            coche.precio = data.get('precio', coche.precio)
            
            session.commit()
            return jsonify({"mensaje": "Coche actualizado"}), 200
        return jsonify({"error": "Coche no encontrado"}), 404

    # 5. DELETE (DELETE): Borrar un coche
    @app.route('/api/coche/<id>', methods=['DELETE'])
    def delete_coche(id):
        coche = session.query(Coche).filter_by(id=id).first()
        if coche:
            session.delete(coche)
            session.commit()
            return jsonify({"mensaje": "Coche eliminado"}), 204
        return jsonify({"error": "Coche no encontrado"}), 404