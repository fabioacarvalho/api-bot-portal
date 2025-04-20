automation_success_response = {
    "tags": ["Automação"],
    "summary": "Inicia a automação com base em NIS, Nome ou CPF",
    "consumes": ["application/json"],
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "input_value": {
                        "type": "string",
                        "example": "João da Silva",
                        "description": "Informe um CPF, NIS ou Nome completo"
                    }
                },
                "required": ["input_value"]
            }
        }
    ],
    "responses": {
        200: {
            "description": "Automação executada com sucesso",
            "examples": {
                "application/json": {
                    "status": "success",
                    "data": {
                        "data_consulta": "2023-10-01_12:00:00",
                        "cpf": "***.000.000-**",
                        "localidade": "Curitiba PR",
                        "nome_completo": "João da Silva",
                        "beneficios": "R$ 1.200,00",
                        "screenshot": "valores em base64",
                        "detalhes": []
                    }
                }
            }
        },
        400: {
            "description": "Requisição inválida - faltando input_value",
            "examples": {
                "application/json": {
                    "error": "Missing 'input_value' in request body, please send NIS, Name or CPF"
                }
            }
        }
    }
}

# automation_success_response = {
#     "responses": {
#         200: {
#             "description": "Automação iniciada com sucesso",
#             "examples": {
#                 "application/json": {
#                     "status": "success",
#                     "message": "Automação iniciada com sucesso.",
#                     "data": []
#                 }
#             }
#         }
#     }
# }
