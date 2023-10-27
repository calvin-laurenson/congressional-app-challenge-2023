import { NavLink, Outlet } from "react-router-dom";
import CameraIconSelected from "@mui/icons-material/PhotoCamera"
import CameraIcon from "@mui/icons-material/PhotoCameraOutlined"
import AttendanceIconSelected from "@mui/icons-material/Ballot"
import AttendanceIcon from "@mui/icons-material/BallotOutlined"
import TeamsIconSelected from "@mui/icons-material/Groups"
import TeamsIcon from "@mui/icons-material/GroupsOutlined"

import React from "react";
export default function Dashboard() {
    return (
        <div className="">
            <div className="w-16 h-full flex flex-col border-r-[1px] border-gray-400 fixed justify-center items-center">
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
                
            </div>
            <Outlet />
        </div>
    )
}