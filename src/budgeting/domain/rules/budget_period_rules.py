from pydantic import BaseModel, model_validator
from datetime import date


class BudgetPeriodSchema(BaseModel):
    start_date: date
    end_date: date

    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_date <= self.start_date:
            raise ValueError("end_date must be greater than start_date")
        return self
