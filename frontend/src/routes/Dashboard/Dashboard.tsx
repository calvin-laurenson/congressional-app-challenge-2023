import { NavLink, Outlet } from "react-router-dom";
import CameraIconSelected from "@mui/icons-material/PhotoCamera"
import CameraIcon from "@mui/icons-material/PhotoCameraOutlined"
import AttendanceIconSelected from "@mui/icons-material/Ballot"
import AttendanceIcon from "@mui/icons-material/BallotOutlined"
import TeamsIconSelected from "@mui/icons-material/Groups"
import TeamsIcon from "@mui/icons-material/GroupsOutlined"

import React, { useCallback, useEffect, useRef, useState } from "react";
// import Camera from "./Camera";
import Attendance, { ClassAttendance, classAttendance } from "./Attendance";
import axios from "axios";
import Webcam from "react-webcam";
import { DropdownMenu, Select, Switch } from "@radix-ui/themes";
import { z } from "zod";

function dataURLtoFile(dataurl: string, filename: string): File {
    var arr = dataurl.split(","),
        mime = arr[0]!!.match(/:(.*?);/)!![1],
        bstr = atob(arr[1]),
        n = bstr.length,
        u8arr = new Uint8Array(n);

    while (n--) {
        u8arr[n] = bstr.charCodeAt(n);
    }
    return new File([u8arr], filename, { type: mime });
}   

const periodclass = z.object({
    id: z.number(),
    name: z.string(),
})

const periodclasses = z.array(periodclass)

const classesByTeacherID = z.object({error: z.null(), periodclasses})

type PeriodClasses = z.infer<typeof periodclasses>

export default function Dashboard() {
    const [attendance, setAttendance] = useState<ClassAttendance>({})
    const [isGettingAttendance, setIsGettingAttendance] = useState(false)
    const [isAttendanceing, setIsAttendanceing] = useState<number | null>(null);

    const [periodclasses, setPeriodclasses] = useState<PeriodClasses | null>(null)

    const [selectedClass, setSelectedClass] = useState<string | undefined>(undefined)

    const updateAttendance = async () => {
        console.log("Updating Attendance")
        if (!isAttendanceing) return
        if (isGettingAttendance) return
        if (selectedClass === undefined) return
        setIsGettingAttendance(true)
        const resp = await axios.get("http://localhost:8000/get_class_attendance", { params: { class_id: selectedClass, start_time: isAttendanceing } })
        const newAttendance = classAttendance.safeParse(resp.data)
        if (newAttendance.success) {
            setAttendance(newAttendance.data)
        }
        setIsGettingAttendance(false)
    }
    // useEffect(() => {updateAttendance()}, [])

    const webcamRef = useRef<Webcam & HTMLVideoElement>(null);
    const capture = useCallback(
        () => {
            const imageSrc = webcamRef.current?.getScreenshot();
            return imageSrc
        },
        [webcamRef]
    );
    const [isCameraing, setIsCameraing] = useState(false);
    const [isTardying, setIsTardying] = useState(false);

    const tardyRef = useRef(false)

    useEffect(() => {
        if (isTardying) {
            tardyRef.current = true
        } else {
            tardyRef.current = false
        }
    }, [isTardying])

    const timeoutID = useRef<number | null>(null)
    const startCapturing = (async () => {
        if (isAttendanceing === null) {
            console.log("Stopping capturing. Attendanceing is ", isAttendanceing);

            return
        }
        console.time("capture")
        const imageSrc = capture()
        console.timeEnd("capture")

        console.time("image-convert")
        const imageFile = dataURLtoFile(imageSrc!!, "image.png")
        console.timeEnd("image-convert")

        const formData = new FormData();
        formData.append("image_file", imageFile);

        console.time("fetch")
        // Send multipart/form-data request
        console.log("Is tardying", isTardying);
        
        const resp = await axios.post("http://localhost:8000/add_image", formData, { params: { time: Date.now(), tardy: tardyRef.current } })
        console.log(resp);
        
        console.timeEnd("fetch")

        if (resp.status === 200 && "error" in resp.data && resp.data.error === null) {
            console.log("Good upload")
            updateAttendance()
        } else {
            console.log("Bad upload", resp.data)
        }
        timeoutID.current = (window.setTimeout(() => startCapturing(), 500))
    })

    useEffect(() => {
        startCapturing()
    }, [isAttendanceing])

    async function onAttendanceSwitch(v: boolean) {
        if (isAttendanceing === null && v) {
            if (timeoutID.current !== null) {
                window.clearTimeout(timeoutID.current)
                timeoutID.current = null
            }
            setIsAttendanceing(Date.now())
        } else {
            console.log("Stopping attendanceing")
            setIsAttendanceing(null)
            if (timeoutID.current !== null) {
                window.clearTimeout(timeoutID.current)
                timeoutID.current = null
            }
        }
    }

    useEffect(() => {
        if (selectedClass === undefined) return
        const resp = axios.get("http://localhost:8000/get_students_in_class", {params: {class_id: selectedClass}}).then((resp) => {
            const parsed = z.array(z.string()).safeParse(resp.data)
            if (parsed.success) {
                const newAttendance: ClassAttendance = {}
                parsed.data.forEach((student) => {
                    newAttendance[student] = "absent"
                })
                setAttendance(newAttendance)
            }
        })

    }, [selectedClass])

    useEffect(() => {
        async function getClasses() {
            const resp = await axios.get("http://localhost:8000/get_classes_by_teacher_id", { params: { teacher_id: 1 } })
            const newPeriodClasses = classesByTeacherID.safeParse(resp.data)
            if (newPeriodClasses.success) {
                setPeriodclasses(newPeriodClasses.data.periodclasses)
            }
        }
        getClasses()
    }, [])

    return (
        <div className="flex flex-row" style={{ flex: "1 1 0px" }}>
            {/* <div className="w-16 h-full flex flex-col border-r-[1px] border-gray-400 fixed justify-center items-center">
                 <NavLink className="w-full" to="camera" children={({isActive}) => {
                    const Comp = isActive ? CameraIconSelected : CameraIcon
                    return (<Comp sx={{height: "fit-content", width: "inherit"}} />)
                 }} />
                 <NavLink className="w-full" to="teams" children={({isActive}) => {
                    const Comp = isActive ? TeamsIconSelected : TeamsIcon
                    return (<Comp sx={{height: "fit-content", width: "inherit", paddingX: "4px"}} />)
                 }} />
                 <NavLink className="w-full" to="attendance" children={({isActive}) => {
                    const Comp = isActive ? AttendanceIconSelected : AttendanceIcon
                    return (<Comp sx={{height: "fit-content", width: "inherit", paddingX: "3px"}} />)
                 }} />
                
            </div> */}

            <div className="">
                <div className="flex flex-row justify-center">
                    <div className="p-2">
                        <Webcam ref={webcamRef} audio={false} videoConstraints={{ facingMode: "user" }} onUserMedia={() => setIsCameraing(true)} />
                        {isCameraing ? (
                            <div className="flex gap-4">
                                <div className="flex flex-col justify-center items-center">
                                    <Select.Root disabled={periodclasses === null || isAttendanceing !== null} onValueChange={setSelectedClass} value={selectedClass}>
                                        <Select.Trigger placeholder="Select a class" />
                                        <Select.Content>
                                            {periodclasses?.map((periodclass) => (
                                                <Select.Item key={periodclass.id} value={periodclass.id.toString()}>{periodclass.name}</Select.Item>
                                            ))}
                                        </Select.Content>
                                    </Select.Root>
                                    </div>
                                <div className="flex flex-col justify-center items-center">
                                    <span>Record Attendance</span>
                                    <Switch disabled={selectedClass===undefined} checked={isAttendanceing !== null} onCheckedChange={onAttendanceSwitch} />
                                </div>
                                {isAttendanceing ? (
                                    <div className="flex flex-col justify-center items-center">
                                        <span>Mark Tardy</span>
                                        <Switch checked={isTardying} onCheckedChange={setIsTardying} />
                                    </div>
                                ) : (<div></div>)}
                            </div>
                        ) : (<div></div>)}
                    </div>
                </div>
            </div>
            <div className="flex-grow">
                <Attendance attendance={attendance} />
            </div>
        </div>
    )
}