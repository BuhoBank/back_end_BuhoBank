from .database import customer_collection
from .models import CustomerModel
from .models import LogInModel
from bson import ObjectId
import bcrypt

async def add_customer(customer_data: CustomerModel) -> dict:
    # Hashear la contraseña antes de almacenarla
    hashed_password = bcrypt.hashpw(customer_data.password.encode('utf-8'), bcrypt.gensalt())
   # Convertir el modelo a un diccionario serializable
    customer_dict = customer_data.dict(by_alias=True)
    customer_dict['password'] = hashed_password.decode('utf-8')  
    del customer_dict['pass_conf']
    customer_dict['uentas_bancarias'] = []
    try:
        result = await customer_collection.insert_one(customer_dict)
        
        # Verificar si la inserción fue exitosa
        if result.inserted_id:
            return True
        else:
            return False
    except Exception as e:
            print(f"Error al insertar el cliente: {e}")
            return False


async def update_customer(credentials: CustomerModel) -> dict:
    # Hashear la nueva contraseña antes de almacenarla
    hashed_password = bcrypt.hashpw(credentials.password.encode('utf-8'), bcrypt.gensalt())

    # Crear el diccionario con los campos a actualizar
    update_data = {
        "user": credentials.user,
        "password": hashed_password.decode('utf-8')
    }

    result = await customer_collection.update_one(
        {"ci": credentials.ci},
        {"$set": update_data}
    )

    if result.modified_count > 0:
       return True
    else:
        return False



async def checkData(credentials: LogInModel) -> bool:
    query = {
        "user": credentials.user
    }
    user = await customer_collection.find_one(query)
    if user is None:
        print(f"Usuario {credentials.user} no encontrado")
        return False
    else:
        print(f"Usuario {credentials.user} encontrado con exito")
    
    hashed_password=user.get('password','')
    if bcrypt.checkpw(credentials.password.encode('utf-8'), hashed_password.encode('utf-8')):
        return True
    else:
        return False
    
#función para verificar que la nueva contraseña cumple con los requisitos mínimos
async def update_password(user_id: str, current_password: str, new_password: str) -> dict:
    # Buscar el usuario por su ID
    customer = await customer_collection.find_one({"_id": ObjectId(user_id)})
    if not customer:
        raise ValueError("Usuario no encontrado")

    # Verificar si la contraseña actual es correcta
    if not bcrypt.checkpw(current_password.encode('utf-8'), customer['password'].encode('utf-8')):
        return {"error_code": "INCORRECT_CURRENT_PASSWORD"}

    # Hashear la nueva contraseña antes de almacenarla
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    
    # Actualizar la contraseña en la base de datos
    await customer_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"password": hashed_password.decode('utf-8')}}
    )
    
    return {"message": "Contraseña cambiada exitosamente"}