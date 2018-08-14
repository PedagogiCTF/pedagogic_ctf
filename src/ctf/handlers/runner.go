package handlers

import (
	"bytes"
	"ctf/config"
	"errors"
	"fmt"
	dcli "github.com/fsouza/go-dockerclient"
	"io"
	"io/ioutil"
	"log"
	"os"
	"path"
	"time"
	)

type Runner struct {
	RunnerType          string
	ContainerId         string
	CodeDir             string
	ChallengeName       string
	ChallengeFolderPath string
	Language            string
	Code                string
	MapDatabase         bool
	client              *dcli.Client
}

const (
	RUNNER_SNIPPET      = "SNIPPET"
	RUNNER_EXPLOITATION = "EXPLOITATION"
	RUNNER_CORRECTION   = "RUNNER_CORRECTION"
	STATUS_EXPLOITABLE  = 3
	STATUS_CHECK_FAILED = 2
	STATUS_FAILED       = 1
	STATUS_SUCCESS      = 0
	STATUS_TIMED_OUT    = -1
)

func RunSnippet(code, language string) (output string, err error) {

	runner := NewRunner(
		dockerClient(),
		language,
		code,
	)
	defer runner.cleanup()

	runner.RunnerType = RUNNER_SNIPPET

	var status int
	status, err = runner.Run("pedagogictf/sandbox", []string{}, 3000)
	if err != nil {
		log.Printf("[E] Error running code: %s\n", err)
		return
	}

	if status == STATUS_TIMED_OUT {
		output = "Execution timed out"
		return
	}

	output, err = runner.getLogs()
	return
}

func RunExploitation(challengeName, language, challengeFolderPath string, args []string) (output string, err error) {

	var extension string
	extension, err = extForLanguage(language)
	if err != nil {
		return
	}

	fileName := fmt.Sprintf("%s.%s", challengeName, extension)
	code, err := ioutil.ReadFile(path.Join(challengeFolderPath, fileName))
	if err != nil {
		return
	}

	runner := NewRunner(
		dockerClient(),
		language,
		string(code[:]),
	)
	defer runner.cleanup()

	runner.RunnerType = RUNNER_EXPLOITATION
	runner.ChallengeFolderPath = challengeFolderPath
	runner.ChallengeName = challengeName

	var status int
	status, err = runner.Run("pedagogictf/exploitation", args, 10000)
	if err != nil {
		log.Printf("[E] Error running code: %s\n", err)
		return
	}

	if status == STATUS_TIMED_OUT {
		output = "Execution timed out"
		return
	}

	output, err = runner.getLogs()

	failedStatus := map[int]bool{
		STATUS_EXPLOITABLE:  true,
		STATUS_CHECK_FAILED: true,
		STATUS_FAILED:       true,
	}
	if failedStatus[status] {
		return output, errors.New(output)
	}

	return
}

func RunCorrection(challengeFolderPath, code, language string) (output string, status int, err error) {

	runner := NewRunner(
		dockerClient(),
		language,
		code,
	)
	defer runner.cleanup()

	runner.RunnerType = RUNNER_CORRECTION
	runner.ChallengeFolderPath = challengeFolderPath

	status, err = runner.Run("pedagogictf/correction", []string{"code"}, 7000)
	if err != nil {
		log.Printf("[E] Error running code: %s\n", err)
		return
	}

	if status == STATUS_TIMED_OUT {
		output = "Execution timed out"
		err = errors.New(output)
		return
	}

	output, err = runner.getLogs()

	failedStatus := map[int]bool{
		STATUS_EXPLOITABLE:  true,
		STATUS_CHECK_FAILED: true,
		STATUS_FAILED:       true,
	}
	if failedStatus[status] {
		err = errors.New(output)
	}

	return
}

func (r *Runner) getLogs() (output string, err error) {

	var buffer bytes.Buffer
	logsOptions := dcli.LogsOptions{
		Container:    r.ContainerId,
		OutputStream: &buffer,
		ErrorStream:  &buffer,
		Stdout:       true,
		Stderr:       true,
	}

	err = r.client.Logs(logsOptions)
	if err != nil {
		log.Println(err)
		return
	}

	output = buffer.String()
	return
}

func dockerClient() *dcli.Client {
	endpoint := "unix:///var/run/docker.sock"
	client, err := dcli.NewClient(endpoint)
	if err != nil {
		panic(err)
	}
	return client
}

func NewRunner(client *dcli.Client, lang string, code string) *Runner {
	return &Runner{Language: lang, Code: code, client: client}
}

func (r *Runner) Run(image string, cmd []string, timeout time.Duration) (int, error) {
	log.Println("Creating code directory")
	if err := r.createCodeDir(); err != nil {
		return 0, err
	}

	log.Println("Creating source file")
	srcFile, err := r.createSrcFile()
	if err != nil {
		return 0, err
	}

	if r.RunnerType == RUNNER_CORRECTION {
		r.copyCorrectionFiles()
		if err != nil {
			return 0, err
		}
	}

	if r.RunnerType == RUNNER_EXPLOITATION {
		r.copyExploitationFiles()
		if err != nil {
			return 0, err
		}
	}

	cmd = append([]string{path.Join("/code", srcFile)}, cmd...)

	log.Println("Creating container")
	if err := r.createContainer(image, cmd); err != nil {
		return 0, err
	}

	log.Println("Starting container")
	if err := r.startContainer(); err != nil {
		return 0, err
	}

	log.Println("Waiting for container to finish")
	killed, status := r.waitForExit(timeout)
	if killed {
		log.Printf("Container exited with status %d\n", status)
		return STATUS_TIMED_OUT, nil
	}

	return status, nil
}

func (r *Runner) createCodeDir() error {
	dir, err := ioutil.TempDir("", "code-")
	r.CodeDir = dir
	return err
}

func (r *Runner) createSrcFile() (string, error) {
	ext, err := extForLanguage(r.Language)
	if err != nil {
		return "", err
	}

	fileName := fmt.Sprintf("prog.%s", ext)
	filePath := path.Join(r.CodeDir, fileName)
	f, err := os.Create(filePath)
	if err != nil {
		return "", err
	}
	defer f.Close()

	if _, err := f.WriteString(r.Code); err != nil {
		return "", err
	}

	return fileName, nil
}

func (r *Runner) copyExploitationFiles() error {
	requiredFiles := []string{
		"secret",
		"key",
		"victim_browser.py",
	}

	for _, fileName := range requiredFiles {
		src := path.Join(r.ChallengeFolderPath, fileName)
		if _, err := os.Stat(src); err == nil {
			dst := path.Join(r.CodeDir, fileName)
			s, err := os.Open(src)
			if err != nil {
				return err
			}
			d, err := os.Create(dst)
			if err != nil {
				return err
			}
			if _, err := io.Copy(d, s); err != nil {
				s.Close()
				d.Close()
				return err
			}
			s.Close()
			d.Close()
		}
	}
	return nil
}

func (r *Runner) copyCorrectionFiles() error {
	requiredFiles := []string{
		"init.py",
		"check.py",
		"exploit.py",
		"victim_browser.py",
	}

	for _, fileName := range requiredFiles {
		src := path.Join(r.ChallengeFolderPath, fileName)
		if _, err := os.Stat(src); err == nil {
			dst := path.Join(r.CodeDir, fileName)
			s, err := os.Open(src)
			if err != nil {
				return err
			}
			d, err := os.Create(dst)
			if err != nil {
				return err
			}
			if _, err := io.Copy(d, s); err != nil {
				s.Close()
				d.Close()
				return err
			}
			s.Close()
			d.Close()
		}
	}
	return nil
}

func (r *Runner) createContainer(image string, cmd []string) error {

	writeLimit := []dcli.BlockLimit{
		{
			Path: config.Conf.LocalDiskLabel,
			Rate: 3000000,
		},
	}

	// The files are written in /tmp in the docker container,
	// but /tmp is mounted to /tmp/guest on the host
	hostPath := fmt.Sprintf("/tmp/guest/%s", path.Base(r.CodeDir))
	binds := []string{fmt.Sprintf("%s:/code", hostPath)}
	if r.RunnerType == RUNNER_EXPLOITATION {
		// Mounting /tmp/guest/chall_name/chall_name.db to /tmp/chall_name/chall_name.db
		binds = append(binds, fmt.Sprintf("/tmp/guest/%s/%s.db:/tmp/%s/%s.db", r.ChallengeName, r.ChallengeName, r.ChallengeName, r.ChallengeName))
	}

	hostConfig := &dcli.HostConfig{
		Binds:               binds,
		BlkioDeviceWriteBps: writeLimit,
		NetworkMode:         "pedagogic_ctf",
		ReadonlyRootfs:      false,
	}

	config := &dcli.Config{
		CPUShares: 2,
		Memory:    2<<28, // 512Mo = 2^9 * 2^20 = 2<<28
		Tty:       false,
		OpenStdin: false,
		Cmd:       cmd,
		Image:     image,
	}

	createOpts := dcli.CreateContainerOptions{
		Config:     config,
		HostConfig: hostConfig,
	}

	container, err := r.client.CreateContainer(createOpts)
	if err != nil {
		return err
	}

	r.ContainerId = container.ID
	return nil
}

func (r *Runner) startContainer() error {
	if r.ContainerId == "" {
		return errors.New("Can't start a container before it is created")
	}

	if err := r.client.StartContainer(r.ContainerId, &dcli.HostConfig{}); err != nil {
		return err
	}

	return nil
}

func (r *Runner) waitForExit(timeoutMs time.Duration) (bool, int) {
	statusChan := make(chan int)
	go func() {
		if status, err := r.client.WaitContainer(r.ContainerId); err != nil {
			log.Println(err)
		} else {
			statusChan <- status
		}
	}()

	killed := false
	for {
		select {
		case status := <-statusChan:
			log.Println("Container exited by itself")
			return killed, status
		case <-time.After(time.Millisecond * timeoutMs):
			log.Println("Container timed out, killing")
			if err := r.client.StopContainer(r.ContainerId, 0); err != nil {
				log.Println(err)
			}
			killed = true
		}
	}
}

func (r *Runner) cleanup() {

	log.Println("Removing container")
	removeOpts := dcli.RemoveContainerOptions{
		ID: r.ContainerId,
	}
	if err := r.client.RemoveContainer(removeOpts); err != nil {
		log.Printf("Couldn't remove container %s (%v)\n", r.ContainerId, err)
	}

	log.Println("Cleanup sandbox")
	if err := os.RemoveAll(r.CodeDir); err != nil {
		log.Printf("Couldn't remove temp dir %s (%v)\n", r.CodeDir, err)
	}
}

func extForLanguage(lang string) (string, error) {
	switch lang {
	case "GOLANG":
		return "go", nil
	case "PERL":
		return "pl", nil
	case "PYTHON":
		return "py", nil
	}
	return "", fmt.Errorf("Invalid language %v", lang)
}
