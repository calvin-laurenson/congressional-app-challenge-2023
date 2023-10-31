import { NavLink, Outlet } from "react-router-dom";
import { Box, Button, Flex } from "@radix-ui/themes";

export default function Home() {
    return (
        <div>

            <div className="h-10 flex flex-row overflow-hidden items-center border-b border-gray-400 gap-3">
                <img src="ClassSync.svg" alt="ClassSync" className="h-[inherit]" />
                <div className=""><b>ClassSync</b></div>
                {/* <img src="ClassSyncText.svg" alt="ClassSync" className="h-[inherit] mt-2 mb-1" style={{ filter: "invert(1)" }} /> */}
                <div className="grow-[4]"></div>
                <NavLink to="/dashboard" children={({ isActive }) => <Button variant={isActive ? "solid" : "soft"} >Dashboard</Button>} />
                <NavLink to="/plagiarism" children={({ isActive }) => <Button variant={isActive ? "solid" : "soft"} className="mr-4" >Plagiarism</Button>} />
                {/* <NavLink to="/timers" children={({ isActive }) => <Button variant={isActive ? "solid" : "soft"} className="mr-4">Timers</Button>} /> */}

            </div>

            <div className="">

                <Outlet />
            </div>
        </div>
    )
}