import React, {useState} from "react";
import axios from 'axios';
import Loading from 'react-simple-loading';

export default function Search() {
	const [inputText, setInputText] = useState("")
	const [inputDate, setInputDate] = useState("1")
	const [inputLength, setInputLength] = useState("10")
	const [inputType, setInputType] = useState("全部")
	const [loading, setLoading] = useState(false)
	const [results, setResults] = useState([])

	const submitHandler = event => {
		event.preventDefault();
		event.target.className += " was-validated";
		if(inputText != ""){
			fetchData()
		}
	};

	const fetchData = async () => {
		setLoading(true)
		const params = {
			search_keyword: inputText,
			num_years: inputDate,
			pdf_min_num_page: inputLength,
			inputType: inputType
		}
		JSON.stringify(params)
		axios.post(`http://8.210.91.108:5000/`, {params})
        .then(res => {
			console.log("fetch done")
			setResults(res.data.list)
        })
        .catch(err => {
            console.log(err);
            alert(err);
        });
	  };

	  

	return (
		<>
		{loading ? 
			<div>
				{results.length == 0
				?
				<Loading/>:
				<div>
				<table className="table">
					<thead>
						<tr>
							<th>Source</th>
							<th>Title</th>
							<th>Date</th>
							<th>Author</th>
							<th>Type</th>
						</tr>
					</thead>
					<tbody>
						{results.map((article, i) => {
							return (
								<tr key={i}>
									<td> {article.source} </td>
									<td> {article.title} </td>
									<td> {article.date} </td>
									<td> {article.org_name} </td>
									<td> {article.doc_type} </td>
								</tr>
							)
						})}
					</tbody>
				</table>
				</div>

				}
			</div>
		:
			<main style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
				<form
         			className="needs-validation"
					onSubmit={submitHandler}
					noValidate
				>
					<div className="company-search">
						<input
							type="text"
							className="form-control"
							placeholder="公司名"
							required
							onChange={(event) => setInputText(event.target.value)}
						></input>
						<div className="invalid-feedback">
							请输入查询公司名.
              			</div>
					</div>

					
					<div className="date-select">
						<div>
							<label htmlFor="date-select" className="h5"> 年份: </label>
						</div>
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
								className ="custom-control-input"
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
								checked={inputDate === "inf"}
								onChange={(event) => setInputDate(event.target.value)}
							/>
							<label className="custom-control-label" htmlFor="year-4"> 不限</label>
						</div>
					</div>


					<div className="length-select">
						<div>
							<label htmlFor="length-select" className="h5"> 页数： </label>
						</div>
						<div className="custom-control custom-radio custom-control-inline">
							<input
								type="radio"
								className="custom-control-input"
								value="10"
								id ="length-1"
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
								checked={inputLength === "inf"}
								onChange={(event) => setInputLength(event.target.value)}
							/>
							<label className="custom-control-label" htmlFor="length-4">不限</label>
						</div>
					</div>

					<div className="type-select">
						<div>
							<label htmlFor="type-select" className="h5"> 资料种类: </label>
						</div>
						<select className="custom-select custom-select-lg mb-3"
						onChange={(event) => setInputType(event.target.value)}
						>
							
							<option value ="Default" selected>全部</option>
							<option value="NEWS">研报</option>
							<option value="REPORT">资讯</option>
						</select>
					</div>

					<button type="submit" className="btn btn-primary">搜索</button>
				</form>
			</main>
			}
		</>
	)
}
