# =========================================
# SUCCESS RESPONSE
# =========================================

def success_response(

    data=None,

    message="Success",

    status=200
):

    return {

        "success": True,

        "message": message,

        "data": data if data else {}

    }, status


# =========================================
# ERROR RESPONSE
# =========================================

def error_response(

    message="Something went wrong",

    status=400
):

    return {

        "success": False,

        "message": message

    }, status