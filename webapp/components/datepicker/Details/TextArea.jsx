


export default function TextArea({ handleInputChange }) {
    return (
      <div>
        <label htmlFor="details" className="block text-sm font-medium leading-5 text-gray-900">
          Add details about the event here!
        </label>
        <div className="mt-2">
          <textarea
            rows={15}
            name="details"
            id="details"
            onChange={handleInputChange}
            className="dark-mode block w-full rounded-md border-0 py-1 px-2 text-white shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
            defaultValue={''}
            placeholder="Details about your event"
          />
        </div>
      </div>
    )
  }