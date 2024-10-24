from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from quizhub.quizes.models import Quiz, Solution
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
# Create your views here.
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from quizhub.quizes.models import Quiz, Solution
from .serializers import SolutionSerializer

@api_view(['GET'])
@permission_classes([AllowAny])
def get_solutions(request, pk):

   quiz = Quiz.objects.get(pk=pk)
   solutions = Solution.objects.filter(quiz=quiz)
   serializer = SolutionSerializer(solutions, many=True)
   return Response(serializer.data)
   
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_solution(request, pk):
    try:
        quiz = Quiz.objects.get(pk=pk)
    except Quiz.DoesNotExist:
        return Response({"detail": "Quiz no encontrado."}, status=status.HTTP_404_NOT_FOUND)

    if quiz.owner == request.user:
        return Response({"detail": "No puedes agregar una solución a tu propio quiz."}, status=status.HTTP_403_FORBIDDEN)

    if Solution.objects.filter(quiz=quiz, user=request.user).exists():
        return Response({"detail": "No puedes publicar otra solución en este quiz."}, status=status.HTTP_403_FORBIDDEN)

    content = request.data.get('content')
    if not content:
        return Response({"detail": "El contenido es obligatorio."}, status=status.HTTP_400_BAD_REQUEST)

    solution = Solution.objects.create(quiz=quiz, user=request.user, content=content)
    quiz.solutions.add(solution)
    quiz.save() 
    return Response({"detail": "Solución creada exitosamente."}, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_solution(request, pk):
    try:
        solution = Solution.objects.get(pk=pk)
    except Solution.DoesNotExist:
        return Response({"detail": "Solución no encontrada."}, status=status.HTTP_404_NOT_FOUND)

    quiz = solution.quiz 

    if solution.user != request.user:
        return Response({"detail": "No puedes eliminar esta solución."}, status=status.HTTP_403_FORBIDDEN)

    solution.delete()
    quiz.solutions.remove(solution)
    quiz.save()
    
    if Solution.objects.filter(quiz=quiz, user=request.user).exists():
        return Response({"detail": "Solución eliminada. No puedes publicar otra solución en este quiz."}, status=status.HTTP_403_FORBIDDEN)
    
    return Response({"detail": "Solución eliminada."}, status=status.HTTP_204_NO_CONTENT)

   
