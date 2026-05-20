from google.cloud import vision
from boilerplate import CoreError
from result import Either, result_fail, result_ok
from google.cloud.vision_v1 import EntityAnnotation


class GoogleCloudVisionServiceError(CoreError):
    def __init__(
        self,
        cause: Exception | None,
        message: str = "Unexpected error in Google Cloud Vision service",
    ):
        super().__init__(cause, message, "google_cloud_vision_service_error")


class GoogleCloudVisionService:
    def __init__(self):
        self.client = vision.ImageAnnotatorAsyncClient()

    async def extract_text_from_image(
        self, content: bytes
    ) -> Either[EntityAnnotation, GoogleCloudVisionServiceError]:
        try:
            request = vision.AnnotateImageRequest(
                image=vision.Image(content=content),
                features=[vision.Feature(type_=vision.Feature.Type.TEXT_DETECTION)],
            )

            response = await self.client.batch_annotate_images(requests=[request])

            annotated_response = response.responses[0]

            if annotated_response.error.message:
                return result_fail(
                    GoogleCloudVisionServiceError(
                        None, f"GCV error: {annotated_response.error.message}"
                    )
                )

            annotations = annotated_response.text_annotations

            if annotations[0].description is None:
                return result_fail(
                    GoogleCloudVisionServiceError(
                        None,
                        "Failed to extract text from image using Google Cloud Vision",
                    )
                )

            return result_ok(annotations[0])

        except Exception as error:
            return result_fail(GoogleCloudVisionServiceError(error))
