from OpenGL.GL import *
from OpenGL.GL import glGetError


GL_ERROR_CODES = {
    GL_INVALID_ENUM: "GL_INVALID_ENUM",
    GL_INVALID_VALUE: "GL_INVALID_VALUE",
    GL_INVALID_OPERATION: "GL_INVALID_OPERATION",
    GL_STACK_OVERFLOW: "GL_STACK_OVERFLOW",
    GL_STACK_UNDERFLOW: "GL_STACK_UNDERFLOW",
    GL_OUT_OF_MEMORY: "GL_OUT_OF_MEMORY",
    GL_INVALID_FRAMEBUFFER_OPERATION: "GL_INVALID_FRAMEBUFFER_OPERATION",
}

def GLCall(gl_func, *args, **kwargs):
    """
    Wrapper for OpenGL function calls to add error-checking.
    
    Parameters:
        gl_func: The OpenGL function to be called
        args: Arguments to pass to the OpenGL function
        kwargs: Keyword arguments to pass to the OpenGL function
    """
    result = gl_func(*args, **kwargs)
    error = glGetError()
    
    if error != GL_NO_ERROR:
        error_name = GL_ERROR_CODES.get(error, f"Unknown Error Code: {error}")
        print(f"OpenGL Error {error} ({error_name}) in call to {gl_func.__name__}")
    
    return result