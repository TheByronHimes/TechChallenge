import { React, useState } from 'react'

import {
  Link
} from 'react-router-dom'

// **************************************************
// UTILS

/**
 * Creates an object of defaults from fields array
 * @param {Array} fields - the fields to be added to a form
 * @return {Object} - format: {fieldName: fieldDefault}
 */
function initializeValuesFromFields (fields) {
  const obj = {}
  fields.forEach((item) => {
    obj[item[1].name] = item[1].initial
  })

  return obj
}

/**
 * Makes a call to the supplied API with fetch and returns the response
 * @param {string} url - API endpoint url
 * @param {string} m - method for the fetch call (GET, POST, etc.)
 * @param {Object} content - contains body object
 * @return {Object} - the response as an object
 */
async function makeAPICall (url, m, content = {}) {
  // Prepare settings for call to API
  const info = {
    method: m,
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json'
    }
  }

  // include CSRF-token and body if doing a POST request
  if (m === 'POST' || m === 'PATCH') {
    info.body = JSON.stringify(content)
  }

  // Make a call to the API
  let dataToReturn = {}
  try {
    const x = await fetch(url, info)
    dataToReturn = await x.json()
    console.log(dataToReturn)
  } catch {
    console.log('Something went wrong.')
  }

  return dataToReturn
}

// Provides a way to convert API data labels to nicer versions
const FIELDNAME_TO_LABEL = {
  access_token: 'Access Token',
  patient_pseudonym: 'Patiend Pseudonym',
  sample_id: 'Sample ID',
  submitter_email: 'Submitter Email',
  collection_date: 'Collection Date',
  status: 'Status',
  test_result: 'Test Result',
  test_date: 'Test Date',
  msg: 'Message'
}

// **************************************************
// FUNCTION COMPONENTS

/**
 * Creates an HTML form with the supplied fields
 * @param {Array} fields - the fields, as objects, to be included in the form.
 * field objects are formatted like {'Input' | 'Select': props}
 * @param {function} stateUpdater - keeps parent informed of field values
 * @param {function} submitFunction - allows parent to control data submission
 */
function GenForm ({ fields, stateUpdater, submitFunction }) {
  // track field values
  const [values, setValues] = useState(initializeValuesFromFields(fields))

  // this function is passed down to the children (input fields)
  const fieldChanged = (fieldName, value) => {
    setValues({ ...values, [fieldName]: value })
    stateUpdater(fieldName, value)
  }

  // create the input fields (needed to handle both inputs and selects)
  const childFields = []
  for (let i = 0; i < fields.length; i++) {
    const field = fields[i]
    const fieldprops = { ...field[1] }
    fieldprops.onChange = fieldChanged
    fieldprops.key = i

    if (field[0] === 'Select') {
      childFields.push(<Select {...fieldprops} />)
    } else if (field[0] === 'Input') {
      childFields.push(<Input {...fieldprops} />)
    }
  };

  const handleSubmit = event => {
    event.preventDefault()
    submitFunction()
  }

  return (
        <div>
            <form className='form' onSubmit={handleSubmit}>
                {childFields}
                <input type='submit' className='submit' value='Submit' />
            </form>
        </div>
  )
}

/**
 * Creates an <input>
 * @param {string} name - the name of the component
 * @param {string} title - string to be used for the field's label
 * @param {function} onChange - function called to keep parent informed of value
 * @param {string} initial - default value for the field
 * @param {Array} attrs - array of html attributes to apply
 * @param {boolean} required - determines if input will have required attribute
 */
function Input ({ name, title, onChange, initial, attrs, required }) {
  const [value, setValue] = useState(initial)

  // capture new state when selection is changed and pass new val up to parent
  const handleChange = (event) => {
    const text = event.target.value
    setValue(event.target.value)
    onChange(name, text)
  }

  if (required) {
    return (
            <label className='label'>
                {title}
                <input
                    className='form-input'
                    name={name}
                    value={value}
                    onChange={handleChange}
                    required="required"
                    {...attrs}
                />
            </label>
    )
  } else {
    return (
            <label className='label'>
                {title}
                <input
                    className='form-input'
                    name={name}
                    value={value}
                    onChange={handleChange}
                    {...attrs}
                />
            </label>
    )
  }
}

/**
 * Creates a Select element for use with forms
 * @param {string} title - String to be used for the field's label
 * @param {Object} options - Contains info needed to make the <option> tags
 * @param {string} name - the name of the field
 * @param {function} onChange - Keeps the parent informed of the field's value
 * @param {string} initial - default value for the field
 * @param {Array} attrs - array of html attributes to apply
 */
function Select ({ title, options, name, onChange, initial, attrs }) {
  // Go through the supplied options and create the corresponding elements
  const createOptions = () => {
    const o = []
    for (let i = 0; i < options.length; i++) {
      o.push(
                <option key={i} value={options[i].val}>
                    {options[i].str}
                </option>
      )
    }
    return o
  }

  const opts = createOptions()
  const [value, setValue] = useState(initial)

  // capture new state when selection is changed and pass new val up to parent
  const handleChange = event => {
    const val = event.target.value
    setValue(event.target.value)
    onChange(name, val)
  }

  return (
        <label className='label'>
            {title}
            <select
                className='form-input'
                name={name}
                value={value}
                onChange={handleChange}
                {...attrs} >
                {opts}
            </select>
        </label>
  )
}

/**
 * Creates a section below the form for displaying API call results
 * @param {Array} content - contains info to display (e.g. ['Name', 'Bob'])
 * @param {string} caption - String to be used for the table's caption
 */
function ResultsSection ({ content, caption }) {
  // expecting content to be a list
  const rows = []

  // add a table row for each item in the list
  content.forEach((item) => {
    rows.push(
            <tr key={item[0]}>
                <th>{FIELDNAME_TO_LABEL[item[0]]}</th>
                <td>{item[1]}</td>
            </tr>
    )
  })

  return (
        <table className='results'>
            <caption>{caption}</caption>
            <tbody>
                {rows}
            </tbody>
        </table>
  )
}

/**
 * Creates the omnipresent navbar for the site
 */
export function Header () {
  return (
        <section className='top-bar'>
            <div className='limiting-container'>
                <section className='nav'>
                    <Link to='/upload' className='nav-item'>
                        Submit a Sample
                    </Link>
                    <Link to='/update' className='nav-item'>
                        Upload Test Result
                    </Link>
                    <Link to='/find' className='nav-item'>
                        Find a Sample
                    </Link>
                </section>
            </div>
        </section>
  )
}

/**
 * Creates the form to upload a new sample for testing
 */
export function SampleUploadForm () {
  const input1props = {
    name: 'patient_pseudonym',
    title: 'Patient Pseudonym',
    placeholder: 'Patient name',
    initial: '',
    required: true,
    attrs: {
      'type': 'text',
      'maxlength': 63,
      'autocomplete': 'off',
      'required': 'required'
    }
  }

  const input2props = {
    name: 'submitter_email',
    title: 'Submitter Email',
    placeholder: 'Your email',
    initial: '',
    required: true,
    attrs: {
      'type': 'email',
      'maxlength': 254,
      'autocomplete': 'on',
      'required': 'required'
    }
  }

  const input3props = {
    name: 'collection_date',
    title: 'Collection Date',
    placeholder: 'Date the sample was taken',
    initial: '',
    required: true,
    attrs: {
      'type': 'datetime-local',
      'required': 'required'
    }
  }

  const fields = [
    ['Input', input1props],
    ['Input', input2props],
    ['Input', input3props]
  ]

  // set up hooks for values, and intialize the values to the fields
  // this is done so unchanged form fields are still captured
  const [values, setValues] = useState(initializeValuesFromFields(fields))
  const [results, setResults] = useState([])

  // gets called by child GenForm and updates this components values
  const stateUpdater = (fieldName, value) => {
    setValues({ ...values, [fieldName]: value })
  }

  // this will fire when the form is submitted
  const subFunc = async () => {
    const content = { ...values }
    const sample = await makeAPICall('sample', 'POST', content)
    setResults(Object.entries(sample))
  }

  return (
        <div>
            <GenForm
                fields={fields}
                stateUpdater={stateUpdater}
                submitFunction={subFunc}
            />
            <br />
            <ResultsSection content={results} caption='Sample Upload Results' />
        </div>
  )
}

/**
 * Creates the form where a lab tech can update test results
 */
export function UpdateForm () {
  const options1 = [
    { val: 'completed', str: 'Complete' },
    { val: 'failed', str: 'Failed' }
  ]

  const options2 = [
    { val: '', str: '' },
    { val: 'positive', str: 'Positive' },
    { val: 'negative', str: 'Negative' }
  ]

  const input1props = {
    name: 'access_token',
    title: 'Access Token',
    initial: '',
    required: true,
    attrs: {
      'type': 'text',
      'placeholder': 'Access Token...',
      'required': 'required'
    }
  }

  const input2props = {
    name: 'test_date',
    title: 'Date and Time of Test',
    initial: '',
    required: true,
    attrs: {
      'type': 'datetime-local',
      'placeholder': '',
      'required': 'required'
    }
  }

  const select1props = {
    title: 'Status',
    name: 'status',
    options: options1,
    initial: 'completed',
    attrs: {
      'required': 'required'
    }
  }

  const select2props = {
    title: 'Result',
    name: 'test_result',
    options: options2,
    initial: '',
    attrs: {
      'required': 'required'
    }
  }

  const fields = [
    ['Input', input1props],
    ['Select', select1props],
    ['Select', select2props],
    ['Input', input2props]
  ]

  // set up hooks for values, and intialize the values to the fields
  // this is done so unchanged form fields are still captured
  const [values, setValues] = useState(initializeValuesFromFields(fields))
  const [results, setResults] = useState([])

  // gets called by child GenForm and updates this components values
  const stateUpdater = (fieldName, value) => {
    console.log('setting', fieldName)
    setValues({ ...values, [fieldName]: value })
    console.log('parent values are now', values)
  }

  // this will fire when the form is submitted
  const subFunc = async () => {
    const content = { ...values }
    console.log(content)
    const sample = await makeAPICall('sample', 'PATCH', content)
    setResults(Object.entries(sample))
  }

  return (
        <div>
            <GenForm
                fields={fields}
                stateUpdater={stateUpdater}
                submitFunction={subFunc}
            />
            <br />
            <ResultsSection content={results} caption='Sample Update Results'/>
        </div>
  )
}

/**
 * Creates the form where doctors can search for tests
 */
export function FindForm () {
  const input1props = {
    name: 'access_token',
    title: 'Access Token',
    initial: '',
    attrs: {
      'type': 'text',
      'id': 'access_token',
      'maxlength': 16,
      'placeholder': 'Access Token...',
      'required': 'required'
    }
  }

  const fields = [
    ['Input', input1props]
  ]

  // set up hooks for values, and intialize the values to the fields
  // this is done so unchanged form fields are still captured
  const [values, setValues] = useState(initializeValuesFromFields(fields))
  const [results, setResults] = useState([])

  // set up a hook for the last execute search to avoid unnecessary calls
  const [lastSearch, setLastSearch] = useState('sample/')

  // gets called by child GenForm and updates this components values
  const stateUpdater = (fieldName, value) => {
    setValues({ ...values, [fieldName]: value })
  }

  // this will fire when the form is submitted
  const subFunc = async () => {
    const url = `sample/${values.access_token}`
    // only perform search if the query is different
    if (url !== lastSearch) {
      const sample = await makeAPICall(url, 'GET')
      setResults(Object.entries(sample))
    }
    setLastSearch(url)
  }

  return (
        <div>
            <GenForm
                fields={fields}
                stateUpdater={stateUpdater}
                submitFunction={subFunc}
            />
            <br />
            <ResultsSection content={results} caption='Search Results'/>
        </div>
  )
}

export function WelcomePage () {
  return (
    <section>
      <h1>COVID-19 PCR Test Management Portal</h1>
      <h2>Please choose from the options above</h2>
    </section>
  )
}
