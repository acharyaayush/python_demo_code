from rest_framework.schemas import AutoSchema
import coreapi

class LoginViewSchema(AutoSchema):
    def get_manual_fields(self, path, method):
        custom_fields = []
        if method.lower() == "post":
            #can pass in Field(name, required, location, schema, description, type, example)
            custom_fields = [
                coreapi.Field("email"),
                coreapi.Field("password"),
                coreapi.Field("device_id"),
                coreapi.Field("device_type"),
                coreapi.Field("device_token"),
            ]
        manual_fields = super().get_manual_fields(path, method)
        return manual_fields + custom_fields


class BookAPISchema(AutoSchema):
    def get_manual_fields(self, path, method):
        custom_fields = []
        if method.lower() == "post":
            custom_fields = [
                coreapi.Field("authorization", location='header'),
                coreapi.Field("user_id"),
                coreapi.Field("cat_id"),
                coreapi.Field("title"),
                coreapi.Field("author"),
                coreapi.Field("publisher"),
                coreapi.Field("pages"),
                coreapi.Field("media_path"),
                coreapi.Field("cover_pic_path"),
                coreapi.Field("public"),
                coreapi.Field("type"),
                coreapi.Field("pic_url"),
                coreapi.Field("audio_url"),
            ]
        if method.lower() == "put":
            custom_fields = [
                coreapi.Field("authorization", location='header'),
                coreapi.Field("book_id"),
                coreapi.Field("book_title"),
                coreapi.Field("book_author"),
                coreapi.Field("book_publisher"),
                coreapi.Field("number_of_pages"),
                coreapi.Field("media_path"),
                coreapi.Field("cover_pic_path"),
                coreapi.Field("is_admin"),
                coreapi.Field("is_public"),
                coreapi.Field("is_approved"),
                coreapi.Field("type"),
                coreapi.Field("is_active"),
            ]
        if method.lower() == "patch":
            custom_fields = [
                coreapi.Field("authorization", location='header'),
                coreapi.Field("page"),
                coreapi.Field("size"),
                coreapi.Field("active"),
            ]
        if method.lower() == "delete":
            custom_fields = [
                coreapi.Field("authorization", location='header'),
                coreapi.Field("book_id", type='integer'),
            ]
        
        manual_fields = super().get_manual_fields(path, method)
        return manual_fields + custom_fields

