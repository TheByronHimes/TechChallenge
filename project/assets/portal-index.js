import React from 'react'
import ReactDOM from 'react-dom/client'
import {
  BrowserRouter,
  Routes,
  Route
} from 'react-router-dom'

import {
  Header,
  SampleUploadForm,
  UpdateForm,
  FindForm,
  WelcomePage
} from './App.js'

const root = ReactDOM.createRoot(
  document.getElementById('root')
)

root.render(
    <BrowserRouter basename='/portal/'>
        <Header />
        <div className='limiting-container'>
            <Routes>
                <Route path='' element={<WelcomePage />} />
                <Route path='upload' element={<SampleUploadForm />} />
                <Route path='update' element={<UpdateForm />} />
                <Route path='find' element={<FindForm />} />
            </Routes>
        </div>
    </BrowserRouter>
)
