from fastapi import FastAPI, File, UploadFile, Header, HTTPException, Depends
from fastapi.security.api_key import APIKeyHeader
import uvicorn
from pydantic import BaseModel
import hashlib
from db import Database

app = FastAPI()
database = Database('carbery_db.db')
x_auth_user = APIKeyHeader(
    name="X-Auth-User",
    auto_error=False
)


class FileHash(BaseModel):
    userId: str
    filename: str
    sha256: str
    md5: str


async def check_auth(
    x_auth_user: str = Depends(x_auth_user)
):
    if not x_auth_user:
        raise HTTPException(
            status_code=401,
            detail='Не авторизован.'
        )

    return x_auth_user


@app.get(
    '/file_hashes​/{hash}',
    response_model=FileHash,
    summary='Получение имени файла по хэшу.',
    status_code=200,
    response_description='OK'
)
async def get_filename(hash: str):
    values = database.get_value(
        '''SELECT * FROM carbery_table
            WHERE sha256=? OR md5=?''',
        (hash, hash)
    )
    if not values:
        raise HTTPException(
            status_code=404,
            detail='Файлы с данным хэшем не найдены.'
        )
    return {
        'userId': values.get('userId'),
        'filename': values.get('filename'),
        'sha256': values.get('sha256'),
        'md5': values.get('md5')
    }


@app.delete(
    '/file_hashes/{hash}',
    response_model=FileHash,
    summary='Удаление хэшей файлов.',
    status_code=200,
    response_description='OK'
)
async def delete_hash(
    hash: str,
    x_auth_user: str = Depends(check_auth)
):
    values = database.get_value(
        '''SELECT * FROM carbery_table
            WHERE userId=? and (sha256=? or md5=?)''',
        (x_auth_user, hash, hash)
        )
    if not values:
        raise HTTPException(
            status_code=404,
            detail='Файлы с данным хэшем не найдены.'
        )
    database.del_value((x_auth_user, hash, hash))


@app.post(
    '/file_hashes',
    response_model=FileHash,
    summary='Добавление хэша файла.',
    status_code=201,
    response_description='OK'
)
async def add_hash(
    file: UploadFile = File(...),
    x_auth_user: str = Depends(check_auth)
):
    userId = x_auth_user
    filename = file.filename
    file = file.file.read()
    md5 = hashlib.md5(file).hexdigest()
    sha256 = hashlib.sha256(file).hexdigest()
    database.add_value((x_auth_user, filename, sha256, md5))
    return {
        'userId': x_auth_user,
        'filename': filename,
        'sha256': sha256,
        'md5': md5
    }

if __name__ == "__main__":
    uvicorn.run(
        'main:app',
        host='localhost',
        port=3000,
        access_log=False
    )
