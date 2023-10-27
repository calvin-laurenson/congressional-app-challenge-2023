import { useState } from 'react'
import './App.css'
import { RouterProvider, createBrowserRouter } from 'react-router-dom'
import { Theme } from '@radix-ui/themes'
import "@radix-ui/themes/styles.css";
import Home from './routes/Home';
import Dashboard from './routes/Dashboard/Dashboard';
import Camera from './routes/Dashboard/Camera';
import Attendance from './routes/Dashboard/Attendance';
import Teams from './routes/Dashboard/Teams';
import {
  QueryClient,
  QueryClientProvider,
} from "react-query"
import Plagiarism from './routes/Plagiarism';

const queryClient = new QueryClient()

function App() {
  const router = createBrowserRouter([
    {
      path: "/",
      element: <Home />,
      children: [
        {
          path: "dashboard",
          element: <Dashboard />,
          children: [
            {
              path: "camera",
              element: <Camera />
            },
            {
              path: "attendance",
              element: <Attendance />
            },
            {
              path: "teams",
              element: <Teams />
            }
          ]
        },
        {
          path: "/plagiarism",
          element: <Plagiarism />
        },
        {
          path: "/timers",
          element: <div>Timers</div>
        }
      ]
    }
  ])
  return (
    <div>
      <Theme>
        <QueryClientProvider client={queryClient}>
          <RouterProvider router={router} />
        </QueryClientProvider>
      </Theme>
    </div>
  )
}

export default App
