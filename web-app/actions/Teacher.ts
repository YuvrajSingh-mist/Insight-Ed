"use server"

import client from "@/db"
export async function TeacherSignup(username:string, firstname:string, lastname:string, password:string, phoneno:string, address:string, email:string){
    try {
        const teacher = await client.teacher.create({
            data:{
                username,
                email,
                firstname,
                lastname,
                phoneno,
                address,
                password
            }
        })
        if(teacher){
            console.log('Teacher created successfully with id: '+teacher.id);
            return teacher.id
        }
    } catch (error) {
        console.log(error);
        return -1
    }
}

export async function TeacherSignin(email:string, password:string) {
    try {
        const teacher = await client.teacher.findUnique({
            where:{
                email,
                password
            }
        })
        if(teacher){
            console.log('Teacher is successfully signed in having the id '+teacher.id);
            return teacher.id;   
        }
    } catch (error) {
        console.log(error);
        return -1;
    }
}

export async function addUploadLink(lectureid: string, UploadLink:string, teacherEmail:string) {
    const lecture = await client.lecture.findUnique({
        where:{
            id:lectureid
        }
    })
    if(lecture){
        const teacher = await client.teacher.findUnique({
            where:{
                email:teacherEmail
            }
        })
        if(teacher){
            const updatedLecture = await client.lecture.update({
                where: {
                  id: lectureid
                },
                data: {
                  link: UploadLink
                }
            })
            console.log(updatedLecture.link);
            return teacher.id;
            
        }else{
            return null
        }
    }else{
        return null;
    }
    
}