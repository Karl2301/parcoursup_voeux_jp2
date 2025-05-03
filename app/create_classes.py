from flask import Flask, render_template
import sqlmodel
from routes import *
from ext_config import app, engine
from SQLClassSQL import *
import datetime
from sqlmodel import Session, select

classes = [('TA','Termiale A'), ('TB','Termiale B'), ('TC','Termiale C'), ('TD','Termiale D'), ('TE','Termiale E'), ('TF','Termiale F'), ('TG','Termiale G')]

def create_all_classes():
    print("Création des classes")
    with Session(engine) as session:
        superieurs = session.exec(select(Superieurs).where(Superieurs.admin == True)).all()
        for superieur in superieurs:
            superieur.niveau_classe = str(json.dumps([classe[0] for classe in classes]))
            print(f"Superieur {superieur.id} a maintenant les classes {superieur.niveau_classe}")
            session.add(superieur)
        session.commit()

    for classe in classes:
        with Session(engine) as session:
            # Vérifier si la classe existe déjà
            existing_classe = session.query(Classes).filter_by(classe=classe[0]).first()
            if not existing_classe:
                print(f"Création de la classe {classe[0]}")
                new_classe = Classes(
                    classe=classe[0],
                    nom=classe[1],
                    created_at=datetime.datetime.now(),
                )
                session.add(new_classe)
                session.commit()
                print(f"Classe {classe[0]} créée")