from . import db

class Department(db.Model):
    __tablename__ = 'departments'
    department_id = db.Column(db.Integer, primary_key=True)
    department_name = db.Column(db.String(100), nullable=False)
    department_description = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Department {self.department_name}>'

"""
components:
  schemas:
    Department:
      type: object
      properties:
        department_id:
          type: integer
          description: 部门ID
        department_name:
          type: string
          description: 部门名称
        department_description:
          type: string
          description: 部门描述
      required:
        - department_name
"""