import React, { useState } from "react";
import axios from 'axios';
import Loading from 'react-simple-loading';
import router from "next/router"

export default function Home() {
	const [inputText, setInputText] = useState("")
	const [inputDate, setInputDate] = useState("1")
	const [inputLength, setInputLength] = useState("10")
	const [inputType, setInputType] = useState("全部")
	const [loading, setLoading] = useState(false)
	const [results, setResults] = useState([])
	const [status, setStatus] = useState(Number())

	const submitHandler = event => {
		event.preventDefault();
		event.target.className += " was-validated";
		if (inputText != "") {
			const params = "search_keyword=" + inputText + "&num_years=" + inputDate + "&pdf_min_num_page=" + inputLength + "&inputType=" + inputType
			router.push("/search?" + params)
		}
	};

	return (
		<div className="vh-100 row m-0 bg-bland-gray" style={{ paddingTop: "30vh" }}>
			<div className="col-12">
				<div className="row justify-content-center">
					<h1>
						小黑工企业信息服务平台
					</h1>
				</div>
				<div className="row justify-content-center">
					<form
						className="needs-validation col-5"
						onSubmit={submitHandler}
						noValidate
					>
						<div className="row">
							<input
								type="text"
								className="form-control col-10"
								placeholder="公司名"
								required
								onChange={(event) => setInputText(event.target.value)}
							></input>
							<button type="submit" className="btn btn-primary col-2">搜索</button>
							<div className="invalid-feedback">
								请输入查询公司名.
              					</div>
						</div>
						{/* <div className="row justify-content-between">
							<div className="date-select">
								<label htmlFor="date-select" className="h5" > 日期:</label>
								<div className="custom-control custom-radio custom-control-inline">
									<input
										type="radio"
										className="custom-control-input"
										value="1"
										id="year-1"
										checked={inputDate === "1"}
										onChange={(event) => setInputDate(event.target.value)}
									/>
									<label className="custom-control-label" htmlFor="year-1">1年内</label>
								</div>

								<div className="custom-control custom-radio custom-control-inline">
									<input
										type="radio"
										className="custom-control-input"
										value="2"
										id="year-2"
										checked={inputDate === "2"}
										onChange={(event) => setInputDate(event.target.value)}
									/>
									<label className="custom-control-label" htmlFor="year-2">2年内</label>
								</div>

								<div className="custom-control custom-radio custom-control-inline">
									<input
										type="radio"
										className="custom-control-input"
										value="3"
										id="year-3"
										checked={inputDate === "3"}
										onChange={(event) => setInputDate(event.target.value)}
									/>
									<label className="custom-control-label" htmlFor="year-3"> 3年内</label>
								</div>

								<div className="custom-control custom-radio custom-control-inline">
									<input
										type="radio"
										className="custom-control-input"
										value="inf"
										id="year-4"
										checked={inputDate === "100"}
										onChange={(event) => setInputDate(event.target.value)}
									/>
									<label className="custom-control-label" htmlFor="year-4"> 不限</label>
								</div>
							</div>
						</div>

						<div className="row justify-content-between">
							<div className="length-select">
								<label htmlFor="length-select" className="h5"> 页数:</label>
								<div className="custom-control custom-radio custom-control-inline">
									<input
										type="radio"
										className="custom-control-input"
										value="10"
										id="length-1"
										checked={inputLength === "10"}
										onChange={(event) => setInputLength(event.target.value)}
									/>
									<label className="custom-control-label" htmlFor="length-1">10页+</label>
								</div>

								<div className="custom-control custom-radio custom-control-inline">
									<input
										type="radio"
										className="custom-control-input"
										value="20"
										id="length-2"
										checked={inputLength === "20"}
										onChange={(event) => setInputLength(event.target.value)}
									/>
									<label className="custom-control-label" htmlFor="length-2">20页+</label>
								</div>
								<div className="custom-control custom-radio custom-control-inline">
									<input
										type="radio"
										className="custom-control-input"
										value="30"
										id="length-3"
										checked={inputLength === "30"}
										onChange={(event) => setInputLength(event.target.value)}
									/>
									<label className="custom-control-label" htmlFor="length-3">30页+</label>
								</div>
								<div className="custom-control custom-radio custom-control-inline">
									<input
										type="radio"
										className="custom-control-input"
										value="inf"
										id="length-4"
										checked={inputLength === "0"}
										onChange={(event) => setInputLength(event.target.value)}
									/>
									<label className="custom-control-label" htmlFor="length-4">不限</label>
								</div>
							</div>
						</div>
						<div className="row pt-1 justify-content-center">
							<div className="type-select">
								<label htmlFor="type-select" className=""> 资料种类: </label>
								<select className="custom-select custom-select-lg"
									onChange={(event) => setInputType(event.target.value)}
								>
									<option value="Default" selected>全部</option>
									<option value="NEWS">研报</option>
									<option value="REPORT">资讯</option>
								</select>
							</div>
						</div> */}
					</form>
				</div>
			</div>
		</div >
	)
}
