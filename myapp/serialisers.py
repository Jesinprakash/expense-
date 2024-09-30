from rest_framework import serializers

from myapp.models import User,Category,Transactions

class UserSerialiser(serializers.ModelSerializer):

    password1=serializers.CharField(write_only=True)

    password2=serializers.CharField(write_only=True)

    password=serializers.CharField(read_only=True)

    class Meta:

        model=User
    
        fields=["id","username","email","password1","password2","password"]

    def create(self, validated_data):

        password1=validated_data.pop("password1")

        password2=validated_data.pop("password2")


        return User.objects.create_user(**validated_data,password=password1)
    
    def validate(self,data):  #for validation override this methode for password conforming

        if data["password1"] != data["password2"]:

            raise serializers.ValidationError("password mismatch")
        
        return data
    

class CategorySerializer(serializers.ModelSerializer):

    owner=serializers.StringRelatedField(read_only=True)

    class Meta:

        model=Category

        fields="__all__"

        read_only_fields=["id","owner"]

class TransactionSerializer(serializers.ModelSerializer):

    owner=serializers.StringRelatedField(read_only=True)

    class Meta:

        model=Transactions

        fields="__all__"

        read_only_fields=["id","created_date","owner"]

