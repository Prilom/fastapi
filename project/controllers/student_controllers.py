import datetime
from fastapi import HTTPException
from project.models.master_model import Master
from project.models.student_model import Student
from project.models.answers_model import Answers


def create_item_master(student_id: str, model_id : int):
    """comprueba si existe el student_id pasado por
    parámetro y si es true crea un registro en la tabla master"""
    student = Student.select().where(Student.student_id == student_id).get()
    if not student:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado para el colegio proporcionado")
    master = Master(
        school_id = student.school_id,
        student_id = student.student_id,
        prediction = None,
        prob_prediction = None,
        model_id = model_id,
        )
    master.save()
    return Master(
        entry_id = master.entry_id,
        school_id= master.school_id,
        student_id = master.student_id,
        prediction= master.prediction,
        prob_prediction = master.prob_prediction,
        comments = master.comments
        )

def save_survey_answers( #Funcion que realiza el guardado en BBDD de las respuestas generadas por los alumnos
        entry_id: str, 
        model_id: int, 
        answers: dict):
    answers_register = Answers(entry_id = entry_id, model_id = model_id, answer_dict= str(answers))
    answers_register.save()
    print(answers_register)
    return Answers(entry_id = answers_register.entry_id, 
                   answer_dict= answers_register.answer_dict)


def save_predict(entry_id, predict):
    #################################
    #codigo para atomizar el predict#
    #################################
    prediction = None
    prob_prediction = None
    entry = Master.select().where(Master.entry_id == entry_id).get()
    entry.prediction = prediction
    entry.prob_prediction = prob_prediction
    entry.dt_update = datetime.utcnow()
    entry.save()
    return {'msg': 'Predicción registrada correctamente'}