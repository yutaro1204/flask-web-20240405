# Flask Web

## コンテナ起動

```zsh
$ docker compose build
$ docker compose up -d
```

## 対話モード

https://flask.palletsprojects.com/en/3.0.x/cli/#open-a-shell

```zsh
$ docker compose run --rm local_app flask shell
```

## Flask-Migrate

https://flask-migrate.readthedocs.io/en/latest/

init は初回のみで良い。
model の追加後は migrate と upgrade をセットで実行する。

```bash
$ flask db init
$ flask db migrate -m 'Migration comment'
$ flask db upgrade
$ flask db downgrade
```

## Flask-SQLAlchemy

https://flask-sqlalchemy.palletsprojects.com/en/3.1.x/
https://docs.sqlalchemy.org/en/20/orm/quickstart.html
https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html
https://docs.sqlalchemy.org/en/20/orm/cascades.html

### DML

https://flask-sqlalchemy.palletsprojects.com/en/3.1.x/queries/

```python
model = Model()
db.session.add(model) # insert
db.session.delete(model) # delete
model.is_flag = True # update
db.session.commit() # commit

# select
model = db.session.execute(db.select(Model).filter_by(column=column)).scalar_one()
models = db.session.execute(db.select(Model).order_by(Model.column)).scalars()
```
