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
import { Switch } from "@radix-ui/themes";

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

export default function Dashboard() {
    const [attendance, setAttendance] = useState<ClassAttendance>({})
    const [isGettingAttendance, setIsGettingAttendance] = useState(false)
    const [isAttendanceing, setIsAttendanceing] = useState<number | null>(null);

    const updateAttendance = async () => {
        console.log("Updating Attendance")
        if (!isAttendanceing) return
        if (isGettingAttendance) return
        setIsGettingAttendance(true)
        const resp = await axios.get("http://localhost:8000/get_class_attendance", { params: { class_id: 1, start_time: isAttendanceing } })
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

    const [timeoutID, setTimeoutID] = useState<number | null>(null)
    async function startCapturing() {
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
        const resp = await axios.post("http://localhost:8000/add_image", formData, { params: { time: Date.now(), tardy: isTardying } })
        console.timeEnd("fetch")

        if (resp.status === 200 && "error" in resp.data && resp.data.error === null) {
            console.log("Good upload")
            updateAttendance()
        } else {
            console.log("Bad upload", resp.data)
        }
        setTimeoutID(window.setTimeout(startCapturing, 500))
    }

    useEffect(() => {
        startCapturing()
    }, [isAttendanceing])

    async function onAttendanceSwitch(v: boolean) {
        if (isAttendanceing === null && v) {
            setIsAttendanceing(Date.now())
        } else {
            setIsAttendanceing(null)
        }
    }

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
                                    <span>Record Attendance   </span>
                                    <Switch checked={isAttendanceing !== null} onCheckedChange={onAttendanceSwitch} />
                                </div>
                                {isAttendanceing ? (
                                    <div className="flex flex-col justify-center items-center">
                                        <span>Mark Tardy</span>
                                        <Switch checked={isTardying} onCheckedChange={setIsTardying} />
                                    </div>
                                ) : (<div></div>)}
                            </div>
                        ) : (<div>Bad</div>)}
                    </div>
                </div>
            </div>
            <div className="flex-grow">
                <Attendance attendance={attendance} />
            </div>
        </div>
    )
}