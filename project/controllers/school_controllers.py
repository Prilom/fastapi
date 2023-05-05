import uuid

from datetime import datetime
from peewee import DoesNotExist, JOIN
from fastapi import HTTPException, Depends

from typing import List

from project.models.student_model import Student
from project.models.school_model import School as SchoolModel
from project.models.master_model import Master
from project.controllers.auth_school import get_user_disabled_current
from typing import List, Dict

def create_students_with_owner(
      db, 
      application:dict,
      current_user:SchoolModel) -> Dict:
      
      students = []
      results ={}
      year = datetime.now().year
      month = datetime.now().month

      for level, courses in application.items():
            results[level] = {}
            for course, classrooms in courses.items():
                  results[level][course] = {}
                  for classroom, count in classrooms.items():
                        results[level][course][classroom] = []
                        student_ids = []
                        for i in range(count):
                              student_id = f"{year}{month:02d}{current_user.school_id:03d}{level[0:3]}{course[-1]}Au{classroom[-1]}{i+1:03d}"
                              student_ids.append(student_id)
                              student = Student(student_id=student_id, school_id=current_user.school_id, date_insert=datetime.utcnow(),credits=0, times_done=0)
                              students.append(student)
                        results[level][course][classroom] = student_ids
      try:
            with db.atomic():
            #con bulk_create hacemos múltiples registros al mismo tiempo en la base de datos
                  Student.bulk_create(students)
      except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
      return results

def survey_date_query(school_id: int):
      """comprueba las diferentes fechas en las que se solicitaron los id para realizar los test para un scholl_id dado"""
      query = Student.select(Student.dt_insert.distinct()).where(Student.school_id == school_id)
       #query = Student.select(fn.DATE_TRUNC('month', Student.dt_insert).alias('month_year')).distinct().where(Student.school_id == school_id)
      return query    

def get_student_info(student_id):
    """metodo que extrae informacion del student_id"""
    levels = {
          'PRI' : 'PRIMARIA',
          'SEC' : 'SECUNDARIA',
          'BAC' : 'BACHILLERATO'
            }

    level = student_id[9:12]
    course = student_id[12:13]
    room = student_id[15:16]
    return {
        'level': levels[level],
        'course': f'Curso {course}',
        'room': f'Aula {room}'
             }

def read_predict(
      school_id: int,
      order_by : str,
      date: str):
      """Método que realiza la consulta sobre las predicciones a la base de datos por fecha"""
      #primero transformamos el parámetro date a datetime 
      date_obj = datetime.strptime(date, "%B - %Y")
      
      order_by_map = {#Creamos un diccionario con las posibles agrupaciones
        'student_id': Master.student_id,
        'prediction': Master.prediction,
        }
      #Realizamos la consulta
      query = (
            Student
            .select(
                  Student.student_id,
                  Master.prediction,
                  Master.prob_prediction
            )
            .join(Master,
                  JOIN.LEFT_OUTER,
                  on=(Master.student_id == Student.student_id).alias('Master')
            )
            .where(
                  (Student.school_id == school_id) &
                  (Student.dt_insert.month == date_obj.month) &
                  (Student.dt_insert.year == date_obj.year)
            ))     
      
      #Creamos el formato de la respuesta
      results = {}
      for record in query:
            student_data = record
            student_id = student_data.student_id
            student_info = get_student_info(student_id)
            #comprobamos que exista la prediccion, de no ser asi, devolvera None
            try:
                  prediction = student_data.Master.prediction
                  prob_prediction = student_data.Master.prob_prediction
            except AttributeError:
                  prediction = None
                  prob_prediction = None
            
            level = student_info['level']
            course = student_info['course']
            room = student_info['room']
            
            if level not in results:
                  results[level] = {}
            if course not in results[level]:
                  results[level][course] = {}
            if room not in results[level][course]:
                  results[level][course][room] = []
           
            
            results[level][course][room].append({
                  'student_id': student_id,
                 'prediction': prediction,
                 'prob_prediction': prob_prediction
            })
            
      # Ordenar estudiantes por id
      if order_by == 'student_id':
        # Ordenar por student_id
        sorted_results = {
            level: {
                course: {
                    room: sorted(results[level][course][room], key=lambda x: x['student_id'])
                    for room in sorted(results[level][course])
                }
                for course in sorted(results[level])
            }
            for level in sorted(results)
        }
      elif order_by == 'prediction':
            # Ordenar por prediction
            sorted_results = {
                  level: {
                  course: {
                        room: sorted(results[level][course][room], 
                                    key=lambda x: (x['prediction'] is None, x['prediction']))
                        for room in sorted(results[level][course])
                  }
                  for course in sorted(results[level])
                  }
                  for level in sorted(results)
            }
      

      return sorted_results






