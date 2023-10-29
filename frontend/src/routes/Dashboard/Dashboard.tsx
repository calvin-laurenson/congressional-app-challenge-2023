import { NavLink, Outlet } from "react-router-dom";
import CameraIconSelected from "@mui/icons-material/PhotoCamera"
import CameraIcon from "@mui/icons-material/PhotoCameraOutlined"
import AttendanceIconSelected from "@mui/icons-material/Ballot"
import AttendanceIcon from "@mui/icons-material/BallotOutlined"
import TeamsIconSelected from "@mui/icons-material/Groups"
import TeamsIcon from "@mui/icons-material/GroupsOutlined"

import React, { useCallback, useEffect, useState } from "react";
import Camera from "./Camera";
import Attendance, { ClassAttendance, classAttendance } from "./Attendance";
import axios from "axios";
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
                <Camera onFrame={updateAttendance} isAttendanceing={isAttendanceing} setIsAttendanceing={setIsAttendanceing} />
            </div>
            <div className="flex-grow">
                <Attendance attendance={attendance} />
            </div>
        </div>
    )
}